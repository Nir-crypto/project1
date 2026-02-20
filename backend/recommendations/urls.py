from django.urls import path
from .views import (
    FeedbackQuestionListView,
    FeedbackSubmitView,
    FailFeedbackOptionsView,
    FailFeedbackSubmitView,
)

urlpatterns = [
    path('feedback/questions', FeedbackQuestionListView.as_view(), name='feedback-questions'),
    path('feedback/submit', FeedbackSubmitView.as_view(), name='feedback-submit'),
    path('feedback/fail-options', FailFeedbackOptionsView.as_view(), name='feedback-fail-options'),
    path('feedback/fail-submit', FailFeedbackSubmitView.as_view(), name='feedback-fail-submit'),
]
