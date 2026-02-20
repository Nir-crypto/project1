from django.urls import path
from .views import RoadmapByCourseView

urlpatterns = [
    path('roadmap/<int:course_id>', RoadmapByCourseView.as_view(), name='roadmap-by-course'),
]
