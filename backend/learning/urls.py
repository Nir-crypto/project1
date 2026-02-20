from django.urls import path
from .views import (
    DashboardView,
    DashboardStatusView,
    CourseListView,
    AssessmentStartView,
    AssessmentAnswerView,
    ResultView,
    FinalAssessmentStartView,
    FinalAssessmentSubmitView,
    FinalAssessmentRetryView,
)

urlpatterns = [
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('dashboard/status', DashboardStatusView.as_view(), name='dashboard-status'),
    path('courses', CourseListView.as_view(), name='courses-list'),
    path('assessment/start', AssessmentStartView.as_view(), name='assessment-start'),
    path('assessment/answer', AssessmentAnswerView.as_view(), name='assessment-answer'),
    path('result/<int:attempt_id>', ResultView.as_view(), name='result'),
    path('final/start', FinalAssessmentStartView.as_view(), name='final-start'),
    path('final/submit', FinalAssessmentSubmitView.as_view(), name='final-submit'),
    path('final/retry', FinalAssessmentRetryView.as_view(), name='final-retry'),
]
