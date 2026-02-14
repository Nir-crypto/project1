from django.contrib import admin
from .models import (
    Course,
    Question,
    AssessmentAttempt,
    AssessmentAnswer,
    FinalAssessmentAttempt,
    UserCourseProgress,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'topic', 'difficulty')
    list_filter = ('topic', 'difficulty')
    search_fields = ('title', 'topic')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'difficulty', 'text')
    list_filter = ('topic', 'difficulty')
    search_fields = ('text',)


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic', 'current_difficulty', 'correct_count', 'overall_points', 'predicted_level')
    list_filter = ('topic', 'current_difficulty', 'predicted_level')


@admin.register(AssessmentAnswer)
class AssessmentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt', 'question', 'selected_option', 'is_correct', 'time_spent')


@admin.register(FinalAssessmentAttempt)
class FinalAssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'score', 'passed', 'attempts_count', 'created_at')


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'status', 'score', 'completed_at')
    list_filter = ('status',)
