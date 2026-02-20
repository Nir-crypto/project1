from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from learning.models import Course, FinalAssessmentAttempt
from .models import FeedbackQuestion, FeedbackResponse
from .serializers import (
    FeedbackQuestionSerializer,
    FeedbackSubmitSerializer,
    FailFeedbackSubmitSerializer,
)


FAIL_FEEDBACK_OPTIONS = [
    'Concepts unclear',
    'Questions too hard',
    'Time insufficient',
    'Need more practice examples',
    'Roadmap not helpful',
]


class FeedbackQuestionListView(APIView):
    def get(self, request):
        questions = FeedbackQuestion.objects.all().order_by('id')
        return Response(FeedbackQuestionSerializer(questions, many=True).data)


class FeedbackSubmitView(APIView):
    def post(self, request):
        serializer = FeedbackSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        course = get_object_or_404(Course, id=data['course_id'])
        final_attempt = (
            FinalAssessmentAttempt.objects.filter(user=request.user, course=course, passed=True)
            .order_by('-created_at')
            .first()
        )
        if not final_attempt:
            return Response(
                {'detail': 'Feedback allowed only after passing final assessment for this course.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if FeedbackResponse.objects.filter(user=request.user, final_attempt=final_attempt).exists():
            return Response(
                {'detail': 'Feedback for this passed final assessment was already submitted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        feedback = FeedbackResponse.objects.create(
            user=request.user,
            course=course,
            final_attempt=final_attempt,
            responses=data['responses'],
            comment=data.get('comment') or '',
            feedback_type='PASS_FEEDBACK',
        )

        return Response({'message': 'Feedback submitted successfully.', 'feedback_id': feedback.id}, status=status.HTTP_201_CREATED)


class FailFeedbackOptionsView(APIView):
    def get(self, request):
        return Response({'options': FAIL_FEEDBACK_OPTIONS})


class FailFeedbackSubmitView(APIView):
    def post(self, request):
        serializer = FailFeedbackSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        course = get_object_or_404(Course, id=data['course_id'])
        final_attempt = get_object_or_404(
            FinalAssessmentAttempt,
            id=data['final_attempt_id'],
            user=request.user,
            course=course,
        )
        latest_attempt = (
            FinalAssessmentAttempt.objects.filter(user=request.user, course=course)
            .order_by('-created_at')
            .first()
        )
        if not latest_attempt or latest_attempt.id != final_attempt.id:
            return Response({'detail': 'Fail feedback is only allowed for the latest attempt.'}, status=status.HTTP_400_BAD_REQUEST)
        if final_attempt.passed:
            return Response({'detail': 'Fail feedback is only allowed for failed attempts.'}, status=status.HTTP_400_BAD_REQUEST)

        if data['selected_option'] not in FAIL_FEEDBACK_OPTIONS:
            return Response({'detail': 'Invalid fail feedback option.'}, status=status.HTTP_400_BAD_REQUEST)

        if FeedbackResponse.objects.filter(
            user=request.user,
            final_attempt=final_attempt,
            feedback_type='FAIL_DIFFICULTY',
        ).exists():
            return Response({'detail': 'Fail feedback already submitted for this attempt.'}, status=status.HTTP_400_BAD_REQUEST)

        feedback = FeedbackResponse.objects.create(
            user=request.user,
            course=course,
            final_attempt=final_attempt,
            responses={'selected_option': data['selected_option']},
            comment='',
            feedback_type='FAIL_DIFFICULTY',
        )
        return Response({'message': 'Fail feedback saved.', 'feedback_id': feedback.id}, status=status.HTTP_201_CREATED)
