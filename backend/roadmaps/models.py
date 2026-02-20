from django.db import models
from django.contrib.auth.models import User
from learning.models import Course


class AIRoadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_roadmaps')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ai_roadmaps')
    current_level = models.CharField(max_length=20)
    overall_points = models.FloatField(default=0)
    interests_snapshot = models.TextField(blank=True)
    generated_by = models.CharField(max_length=50, default='LocalAI')
    prompt_signature = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=10, default='v1')

    def __str__(self):
        return f"Roadmap {self.id} - {self.user.email} - {self.course.title}"


class AIRoadmapStep(models.Model):
    roadmap = models.ForeignKey(AIRoadmap, on_delete=models.CASCADE, related_name='steps')
    step_no = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    est_time_hours = models.FloatField(default=1)
    outcome = models.TextField()
    resource_title = models.CharField(max_length=255, blank=True)
    resource_url = models.URLField(blank=True)

    class Meta:
        ordering = ['step_no']

    def __str__(self):
        return f"Step {self.step_no} - {self.title}"
