from django.urls import path
from .views import FeedbackQuestionListView, FeedbackSubmitView

urlpatterns = [
    path('feedback/questions', FeedbackQuestionListView.as_view(), name='feedback-questions'),
    path('feedback/submit', FeedbackSubmitView.as_view(), name='feedback-submit'),
]
