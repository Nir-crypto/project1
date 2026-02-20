from django.contrib import admin
from .models import AIRoadmap, AIRoadmapStep


class AIRoadmapStepInline(admin.TabularInline):
    model = AIRoadmapStep
    extra = 0


@admin.register(AIRoadmap)
class AIRoadmapAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'current_level', 'overall_points', 'generated_by', 'created_at')
    list_filter = ('current_level', 'generated_by', 'version')
    inlines = [AIRoadmapStepInline]
