from rest_framework import serializers


class AIRoadmapStepSerializer(serializers.Serializer):
    step_no = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    est_time_hours = serializers.FloatField()
    outcome = serializers.CharField()
    resource_title = serializers.CharField(allow_blank=True)
    resource_url = serializers.CharField(allow_blank=True)


class AIRoadmapSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    current_level = serializers.CharField()
    overall_points = serializers.FloatField()
    generated_by = serializers.CharField()
    version = serializers.CharField()
    created_at = serializers.DateTimeField()
    steps = AIRoadmapStepSerializer(many=True)
