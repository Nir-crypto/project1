from rest_framework import serializers
from .models import Course, Question


class CourseSerializer(serializers.ModelSerializer):
    why_recommended = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'topic', 'difficulty', 'description', 'url', 'why_recommended')


class QuestionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'topic', 'difficulty', 'text', 'option_a', 'option_b', 'option_c', 'option_d')


class AssessmentStartSerializer(serializers.Serializer):
    selected_course_id = serializers.IntegerField()


class AssessmentAnswerSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    selected_option = serializers.CharField(max_length=1)
    time_spent = serializers.FloatField(min_value=0)


class FinalAssessmentStartSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()


class FinalAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option = serializers.CharField(max_length=1)


class FinalAssessmentSubmitSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    answers = FinalAnswerItemSerializer(many=True)
    final_attempt_id = serializers.IntegerField(required=False)


class FinalRetrySerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
