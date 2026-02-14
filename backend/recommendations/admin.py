from django.contrib import admin
from .models import RecommendationLog, FeedbackQuestion, FeedbackResponse


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt', 'created_at')


@admin.register(FeedbackQuestion)
class FeedbackQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'type')


@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'final_attempt', 'created_at')
