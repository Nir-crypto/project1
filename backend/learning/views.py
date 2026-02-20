from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recommendations.models import RecommendationLog
from recommendations.services import infer_level_and_recommend
from roadmaps.services import get_or_generate_roadmap

from .models import (
    AssessmentAnswer,
    AssessmentAttempt,
    Course,
    FinalAssessmentAttempt,
    Question,
    UserCourseProgress,
)
from .serializers import (
    AssessmentAnswerSerializer,
    AssessmentStartSerializer,
    CourseSerializer,
    FinalAssessmentStartSerializer,
    FinalAssessmentSubmitSerializer,
    FinalRetrySerializer,
    QuestionPublicSerializer,
)
from .utils import clamp_difficulty, compute_overall_points, safe_option


def _completed_courses_payload(user):
    completed = (
        UserCourseProgress.objects.filter(user=user, status='COMPLETED')
        .select_related('course')
        .order_by('-completed_at')
    )
    return [
        {
            'id': item.course.id,
            'title': item.course.title,
            'topic': item.course.topic,
            'difficulty': item.course.difficulty,
            'score': item.score,
            'completed_at': item.completed_at,
        }
        for item in completed
    ]


def _pending_final_payload(user):
    completed_course_ids = set(
        UserCourseProgress.objects.filter(user=user, status='COMPLETED').values_list('course_id', flat=True)
    )

    latest_failed = (
        FinalAssessmentAttempt.objects.filter(user=user, passed=False)
        .exclude(course_id__in=completed_course_ids)
        .select_related('course')
        .order_by('-created_at')
        .first()
    )
    if latest_failed:
        return {
            'course_id': latest_failed.course.id,
            'course_title': latest_failed.course.title,
            'last_attempt_id': latest_failed.id,
        }

    in_progress = (
        UserCourseProgress.objects.filter(user=user, status='IN_PROGRESS')
        .exclude(course_id__in=completed_course_ids)
        .select_related('course')
        .order_by('-id')
        .first()
    )
    if in_progress:
        last_attempt = (
            FinalAssessmentAttempt.objects.filter(user=user, course=in_progress.course)
            .order_by('-created_at')
            .first()
        )
        return {
            'course_id': in_progress.course.id,
            'course_title': in_progress.course.title,
            'last_attempt_id': last_attempt.id if last_attempt else None,
        }

    return None


def _attach_roadmaps(user, courses, current_level, overall_points):
    interests_list = list(user.profile.interests.values_list('name', flat=True))
    with_roadmaps = []
    for item in courses[:3]:
        course = Course.objects.filter(id=item['id']).first()
        if not course:
            continue
        roadmap = get_or_generate_roadmap(
            user=user,
            course=course,
            current_level=current_level,
            overall_points=overall_points,
            interests_list=interests_list,
        )
        row = dict(item)
        row['roadmap'] = roadmap
        with_roadmaps.append(row)
    return with_roadmaps


def _final_questions_for_course(course):
    questions = list(
        Question.objects.filter(topic__iexact=course.topic, difficulty=course.difficulty)
        .order_by('?')[: settings.FINAL_ASSESSMENT_QUESTIONS]
    )
    if len(questions) < settings.FINAL_ASSESSMENT_QUESTIONS:
        fill_count = settings.FINAL_ASSESSMENT_QUESTIONS - len(questions)
        fallback = list(
            Question.objects.filter(topic__iexact=course.topic)
            .exclude(id__in=[q.id for q in questions])
            .order_by('?')[:fill_count]
        )
        questions.extend(fallback)
    return questions


class DashboardView(APIView):
    def get(self, request):
        completed_courses = _completed_courses_payload(request.user)
        total_courses = Course.objects.count() or 1
        completion_rate = round((len(completed_courses) / total_courses) * 100, 2)
        return Response(
            {
                'current_level': request.user.profile.current_level,
                'completed_courses': completed_courses,
                'progress_stats': {
                    'completed_count': len(completed_courses),
                    'total_courses': total_courses,
                    'completion_rate': completion_rate,
                },
            }
        )


class DashboardStatusView(APIView):
    def get(self, request):
        return Response(
            {
                'current_level': request.user.profile.current_level,
                'completed_courses': _completed_courses_payload(request.user),
                'pending_final': _pending_final_payload(request.user),
            }
        )


class CourseListView(APIView):
    def get(self, request):
        courses = Course.objects.all().order_by('topic', 'difficulty', 'title')
        return Response(CourseSerializer(courses, many=True).data)


class AssessmentStartView(APIView):
    def post(self, request):
        serializer = AssessmentStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = get_object_or_404(Course, id=serializer.validated_data['selected_course_id'])
        initial_difficulty = 'easy'

        question = (
            Question.objects.filter(topic__iexact=course.topic, difficulty=initial_difficulty)
            .order_by('?')
            .first()
        )
        if not question:
            return Response({'detail': 'No questions available for this course topic.'}, status=status.HTTP_400_BAD_REQUEST)

        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            selected_course=course,
            topic=course.topic,
            total_questions=settings.ASSESSMENT_TOTAL_QUESTIONS,
            current_difficulty=initial_difficulty,
            predicted_level=request.user.profile.current_level,
            current_level=request.user.profile.current_level,
        )

        progress, _ = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
        if progress.status != 'COMPLETED':
            progress.status = 'IN_PROGRESS'
            progress.save()

        return Response(
            {
                'attempt_id': attempt.id,
                'question': QuestionPublicSerializer(question).data,
                'progress': {'index': 1, 'total': attempt.total_questions},
                'current_level': request.user.profile.current_level,
                'selected_course': {'id': course.id, 'title': course.title, 'topic': course.topic},
            },
            status=status.HTTP_201_CREATED,
        )


class AssessmentAnswerView(APIView):
    def post(self, request):
        serializer = AssessmentAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        attempt = get_object_or_404(AssessmentAttempt, id=data['attempt_id'], user=request.user)
        if attempt.finished_at is not None:
            return Response({'detail': 'Attempt has already finished.'}, status=status.HTTP_400_BAD_REQUEST)

        question = get_object_or_404(Question, id=data['question_id'])
        if question.topic.lower() != attempt.topic.lower():
            return Response({'detail': 'Question topic mismatch.'}, status=status.HTTP_400_BAD_REQUEST)

        selected = safe_option(data['selected_option'])
        if not selected:
            return Response({'detail': 'Invalid selected_option.'}, status=status.HTTP_400_BAD_REQUEST)

        if AssessmentAnswer.objects.filter(attempt=attempt, question=question).exists():
            return Response({'detail': 'Question already answered in this attempt.'}, status=status.HTTP_400_BAD_REQUEST)

        is_correct = selected == question.correct_option.lower()
        AssessmentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option=selected,
            is_correct=is_correct,
            time_spent=data['time_spent'],
        )

        attempt.correct_count += 1 if is_correct else 0
        attempt.total_time += float(data['time_spent'])
        attempt.current_difficulty = clamp_difficulty(attempt.current_difficulty, is_correct)
        attempt.save()

        answered_ids = list(attempt.answers.values_list('question_id', flat=True))
        answered_count = len(answered_ids)

        def finalize_attempt(total_questions):
            correctness = list(attempt.answers.values_list('is_correct', flat=True))
            attempt.finished_at = timezone.now()
            attempt.total_questions = total_questions
            attempt.overall_points = compute_overall_points(
                correct_count=attempt.correct_count,
                total_questions=attempt.total_questions,
                total_time=attempt.total_time,
                correctness=correctness,
                target_time=settings.TARGET_TIME_PER_QUESTION,
            )

            current_level, courses = infer_level_and_recommend(
                topic=attempt.topic,
                correct_count=attempt.correct_count,
                total_questions=attempt.total_questions,
                total_time=attempt.total_time,
                correctness=correctness,
                top_k=3,
            )
            recommended_with_roadmaps = _attach_roadmaps(
                request.user,
                courses,
                current_level=current_level,
                overall_points=attempt.overall_points,
            )

            attempt.predicted_level = current_level
            attempt.current_level = current_level
            attempt.save()

            profile = request.user.profile
            profile.current_level = current_level
            profile.save()

            RecommendationLog.objects.create(attempt=attempt, courses_json=recommended_with_roadmaps)

            return Response(
                {
                    'done': True,
                    'overall_points': attempt.overall_points,
                    'current_level': current_level,
                    'recommended_courses': recommended_with_roadmaps,
                }
            )

        if answered_count >= attempt.total_questions:
            return finalize_attempt(attempt.total_questions)

        next_question = (
            Question.objects.filter(topic__iexact=attempt.topic, difficulty=attempt.current_difficulty)
            .exclude(id__in=answered_ids)
            .order_by('?')
            .first()
        )

        if not next_question:
            next_question = (
                Question.objects.filter(topic__iexact=attempt.topic)
                .exclude(id__in=answered_ids)
                .order_by('?')
                .first()
            )

        if not next_question:
            return finalize_attempt(answered_count)

        return Response(
            {
                'done': False,
                'is_correct': is_correct,
                'new_difficulty': attempt.current_difficulty,
                'next_question': QuestionPublicSerializer(next_question).data,
                'progress': {'index': answered_count + 1, 'total': attempt.total_questions},
            }
        )


class ResultView(APIView):
    def get(self, request, attempt_id):
        attempt = get_object_or_404(AssessmentAttempt, id=attempt_id, user=request.user)
        latest_log = RecommendationLog.objects.filter(attempt=attempt).order_by('-created_at').first()
        recommended = latest_log.courses_json[:3] if latest_log else []

        return Response(
            {
                'overall_points': attempt.overall_points,
                'current_level': attempt.current_level or attempt.predicted_level,
                'recommended_courses': recommended,
            }
        )


class FinalAssessmentStartView(APIView):
    def post(self, request):
        serializer = FinalAssessmentStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(Course, id=serializer.validated_data['course_id'])

        questions = _final_questions_for_course(course)
        if not questions:
            return Response({'detail': 'No questions available for this course topic.'}, status=status.HTTP_400_BAD_REQUEST)

        progress, _ = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
        if progress.status != 'COMPLETED':
            progress.status = 'IN_PROGRESS'
            progress.save()

        return Response(
            {
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'topic': course.topic,
                    'difficulty': course.difficulty,
                },
                'questions': QuestionPublicSerializer(questions, many=True).data,
            }
        )


class FinalAssessmentSubmitView(APIView):
    def post(self, request):
        serializer = FinalAssessmentSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        course = get_object_or_404(Course, id=data['course_id'])

        answers = data['answers']
        if not answers:
            return Response({'detail': 'Answers are required.'}, status=status.HTTP_400_BAD_REQUEST)

        question_ids = [item['question_id'] for item in answers]
        unique_question_ids = set(question_ids)
        if len(question_ids) != len(unique_question_ids):
            return Response({'detail': 'Duplicate question IDs are not allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        question_map = {
            q.id: q
            for q in Question.objects.filter(id__in=unique_question_ids, topic__iexact=course.topic)
        }
        if len(question_map) != len(unique_question_ids):
            return Response(
                {'detail': 'One or more submitted questions are invalid for this course.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        correct_count = 0
        for answer in answers:
            q = question_map.get(answer['question_id'])
            selected = safe_option(answer['selected_option'])
            if selected and selected == q.correct_option.lower():
                correct_count += 1

        score = round((correct_count / len(answers)) * 100, 2)
        passed = score >= 60

        final_attempt = None
        final_attempt_id = data.get('final_attempt_id')
        if final_attempt_id:
            final_attempt = get_object_or_404(
                FinalAssessmentAttempt,
                id=final_attempt_id,
                user=request.user,
                course=course,
            )
            final_attempt.score = score
            final_attempt.passed = passed
            final_attempt.save()
        else:
            previous_attempts = FinalAssessmentAttempt.objects.filter(user=request.user, course=course).count()
            final_attempt = FinalAssessmentAttempt.objects.create(
                user=request.user,
                course=course,
                score=score,
                passed=passed,
                attempts_count=previous_attempts + 1,
            )

        progress, _ = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
        progress.score = score
        if passed:
            progress.status = 'COMPLETED'
            progress.completed_at = timezone.now()
        else:
            progress.status = 'IN_PROGRESS'
        progress.save()

        message = 'Assessment passed. You can now provide feedback.' if passed else 'Try again. You did not meet the pass threshold.'

        return Response(
            {
                'passed': passed,
                'score': score,
                'message': message,
                'final_attempt_id': final_attempt.id,
                'next_action': 'PASS_FEEDBACK' if passed else 'FAIL_FEEDBACK',
            }
        )


class FinalAssessmentRetryView(APIView):
    def post(self, request):
        serializer = FinalRetrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(Course, id=serializer.validated_data['course_id'])

        last_failed = (
            FinalAssessmentAttempt.objects.filter(user=request.user, course=course, passed=False)
            .order_by('-created_at')
            .first()
        )
        if not last_failed:
            return Response({'detail': 'No failed attempt found for retry.'}, status=status.HTTP_400_BAD_REQUEST)

        completed = UserCourseProgress.objects.filter(user=request.user, course=course, status='COMPLETED').exists()
        if completed:
            return Response({'detail': 'Course is already completed.'}, status=status.HTTP_400_BAD_REQUEST)

        retry_attempt = FinalAssessmentAttempt.objects.create(
            user=request.user,
            course=course,
            score=0,
            passed=False,
            attempts_count=last_failed.attempts_count + 1,
        )

        questions = _final_questions_for_course(course)
        if not questions:
            return Response({'detail': 'No questions available for retry.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'course': {'id': course.id, 'title': course.title, 'topic': course.topic, 'difficulty': course.difficulty},
                'final_attempt_id': retry_attempt.id,
                'questions': QuestionPublicSerializer(questions, many=True).data,
            }
        )
