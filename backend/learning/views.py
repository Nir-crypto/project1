from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Interest
from recommendations.models import RecommendationLog
from recommendations.services import infer_level_and_recommend

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
    FinalAssessmentStartSerializer,
    FinalAssessmentSubmitSerializer,
    QuestionPublicSerializer,
)
from .utils import clamp_difficulty, compute_overall_points, safe_option


class DashboardView(APIView):
    def get(self, request):
        profile = request.user.profile
        completed = (
            UserCourseProgress.objects.filter(user=request.user, status='COMPLETED')
            .select_related('course')
            .order_by('-completed_at')
        )

        completed_courses = [
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

        total_courses = Course.objects.count() or 1
        completion_rate = round((len(completed_courses) / total_courses) * 100, 2)

        return Response(
            {
                'current_level': profile.current_level,
                'completed_courses': completed_courses,
                'progress_stats': {
                    'completed_count': len(completed_courses),
                    'total_courses': total_courses,
                    'completion_rate': completion_rate,
                },
            }
        )


class AssessmentStartView(APIView):
    def post(self, request):
        serializer = AssessmentStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interest = get_object_or_404(Interest, id=serializer.validated_data['interest_id'])
        if not request.user.profile.interests.filter(id=interest.id).exists():
            return Response(
                {'detail': 'You can only start assessments for your selected interests.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        initial_difficulty = 'easy'

        question = (
            Question.objects.filter(topic__iexact=interest.name, difficulty=initial_difficulty)
            .order_by('?')
            .first()
        )
        if not question:
            return Response({'detail': 'No questions available for this interest.'}, status=status.HTTP_400_BAD_REQUEST)

        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            topic=interest.name,
            total_questions=settings.ASSESSMENT_TOTAL_QUESTIONS,
            current_difficulty=initial_difficulty,
            predicted_level=request.user.profile.current_level,
        )

        return Response(
            {
                'attempt_id': attempt.id,
                'question': QuestionPublicSerializer(question).data,
                'progress': {'index': 1, 'total': attempt.total_questions},
                'current_level': request.user.profile.current_level,
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

        if answered_count >= attempt.total_questions:
            attempt.finished_at = timezone.now()
            correctness = list(attempt.answers.values_list('is_correct', flat=True))
            attempt.overall_points = compute_overall_points(
                correct_count=attempt.correct_count,
                total_questions=attempt.total_questions,
                total_time=attempt.total_time,
                correctness=correctness,
                target_time=settings.TARGET_TIME_PER_QUESTION,
            )

            predicted_level, courses = infer_level_and_recommend(
                topic=attempt.topic,
                correct_count=attempt.correct_count,
                total_questions=attempt.total_questions,
                total_time=attempt.total_time,
                correctness=correctness,
            )
            attempt.predicted_level = predicted_level
            attempt.save()

            profile = request.user.profile
            profile.current_level = predicted_level
            profile.save()

            RecommendationLog.objects.create(
                attempt=attempt,
                courses_json=courses,
            )

            return Response(
                {
                    'done': True,
                    'overall_points': attempt.overall_points,
                    'current_level': predicted_level,
                    'recommended_courses': courses,
                }
            )

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
            attempt.finished_at = timezone.now()
            attempt.total_questions = answered_count
            correctness = list(attempt.answers.values_list('is_correct', flat=True))
            attempt.overall_points = compute_overall_points(
                correct_count=attempt.correct_count,
                total_questions=attempt.total_questions,
                total_time=attempt.total_time,
                correctness=correctness,
                target_time=settings.TARGET_TIME_PER_QUESTION,
            )
            predicted_level, courses = infer_level_and_recommend(
                topic=attempt.topic,
                correct_count=attempt.correct_count,
                total_questions=attempt.total_questions,
                total_time=attempt.total_time,
                correctness=correctness,
            )
            attempt.predicted_level = predicted_level
            attempt.save()
            request.user.profile.current_level = predicted_level
            request.user.profile.save()
            RecommendationLog.objects.create(attempt=attempt, courses_json=courses)

            return Response(
                {
                    'done': True,
                    'overall_points': attempt.overall_points,
                    'current_level': predicted_level,
                    'recommended_courses': courses,
                }
            )

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
        recommended = latest_log.courses_json if latest_log else []

        return Response(
            {
                'overall_points': attempt.overall_points,
                'current_level': attempt.predicted_level,
                'recommended_courses': recommended,
            }
        )


class FinalAssessmentStartView(APIView):
    def post(self, request):
        serializer = FinalAssessmentStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(Course, id=serializer.validated_data['course_id'])

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

        if not questions:
            return Response(
                {'detail': 'No questions available for this course topic.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            }
        )
