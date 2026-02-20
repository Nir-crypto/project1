from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Interest, UserProfile


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'name')


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    status = serializers.ChoiceField(choices=UserProfile.STATUS_CHOICES)
    password = serializers.CharField(write_only=True, min_length=6)
    interests = serializers.ListField(child=serializers.IntegerField(), min_length=2)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value.lower().strip()

    def validate_interests(self, value):
        unique_ids = list(dict.fromkeys(value))
        if len(unique_ids) < 2:
            raise serializers.ValidationError('Please select at least 2 interests.')
        existing_count = Interest.objects.filter(id__in=unique_ids).count()
        if existing_count != len(unique_ids):
            raise serializers.ValidationError('One or more selected interests are invalid.')
        return unique_ids

    def validate_phone_number(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('Phone number is required.')
        if cleaned.startswith('+'):
            digits = cleaned[1:]
        else:
            digits = cleaned
        if not digits.isdigit() or len(digits) < 10 or len(digits) > 15:
            raise serializers.ValidationError('Phone number must be 10-15 digits and may start with +.')
        return cleaned

    def create(self, validated_data):
        interests = validated_data.pop('interests')
        name = validated_data.pop('name').strip()
        email = validated_data.pop('email').strip().lower()
        phone_number = validated_data.pop('phone_number').strip()
        status = validated_data.pop('status')

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name,
            password=validated_data['password'],
        )

        profile = user.profile
        profile.name = name
        profile.phone_number = phone_number
        profile.status = status
        profile.save()
        profile.interests.set(interests)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('name', 'email', 'phone_number', 'status', 'interests', 'current_level')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'}) from exc

        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})

        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['name'] = user.profile.name if hasattr(user, 'profile') else user.first_name

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user.profile).data,
        }
