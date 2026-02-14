from django.urls import path
from .views import InterestListView, RegisterView, MeView

urlpatterns = [
    path('interests', InterestListView.as_view(), name='interests-list'),
    path('auth/register', RegisterView.as_view(), name='auth-register'),
    path('auth/me', MeView.as_view(), name='auth-me'),
]
