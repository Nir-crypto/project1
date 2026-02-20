from rest_framework import serializers
from .models import FeedbackQuestion


class FeedbackQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = ('id', 'question_text', 'type', 'options')


class FeedbackSubmitSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    responses = serializers.DictField()
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class FailFeedbackSubmitSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    final_attempt_id = serializers.IntegerField()
    selected_option = serializers.CharField(max_length=100)
