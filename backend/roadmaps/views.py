from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from learning.models import Course
from .services import get_latest_or_generate_for_course


class RoadmapByCourseView(APIView):
    def get(self, request, course_id):
        get_object_or_404(Course, id=course_id)
        payload = get_latest_or_generate_for_course(request.user, course_id)
        return Response(payload)
