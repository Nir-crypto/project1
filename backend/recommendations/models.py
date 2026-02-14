from django.db import models
from django.contrib.auth.models import User
from learning.models import AssessmentAttempt, Course, FinalAssessmentAttempt


class RecommendationLog(models.Model):
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='recommendation_logs')
    courses_json = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RecommendationLog {self.id}"


class FeedbackQuestion(models.Model):
    TYPE_CHOICES = (
        ('RADIO', 'RADIO'),
        ('SCALE', 'SCALE'),
    )

    question_text = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    options = models.JSONField(default=list)

    def __str__(self):
        return self.question_text[:50]


class FeedbackResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_responses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback_responses')
    final_attempt = models.ForeignKey(FinalAssessmentAttempt, on_delete=models.CASCADE, related_name='feedback_responses')
    responses = models.JSONField(default=dict)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} - {self.user.email}"
