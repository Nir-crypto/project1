from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'easy'),
        ('medium', 'medium'),
        ('hard', 'hard'),
    )

    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    description = models.TextField()
    url = models.URLField(max_length=500)

    def __str__(self):
        return self.title


class Question(models.Model):
    DIFFICULTY_CHOICES = Course.DIFFICULTY_CHOICES

    topic = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.topic} [{self.difficulty}]"


class AssessmentAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    selected_course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='assessment_attempts')
    topic = models.CharField(max_length=100)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    current_difficulty = models.CharField(max_length=10, choices=Course.DIFFICULTY_CHOICES, default='easy')
    total_questions = models.PositiveIntegerField(default=10)
    correct_count = models.PositiveIntegerField(default=0)
    total_time = models.FloatField(default=0)
    overall_points = models.FloatField(default=0)
    predicted_level = models.CharField(max_length=20, default='Beginner')
    current_level = models.CharField(max_length=20, default='Beginner')

    def __str__(self):
        return f"Attempt {self.id} - {self.user.email}"


class AssessmentAnswer(models.Model):
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)
    time_spent = models.FloatField(default=0)

    def __str__(self):
        return f"Answer {self.id} - Attempt {self.attempt_id}"


class FinalAssessmentAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='final_attempts')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='final_attempts')
    score = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Final {self.id} - {self.user.email} - {self.course.title}"


class UserCourseProgress(models.Model):
    STATUS_CHOICES = (
        ('IN_PROGRESS', 'IN_PROGRESS'),
        ('COMPLETED', 'COMPLETED'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.status})"
