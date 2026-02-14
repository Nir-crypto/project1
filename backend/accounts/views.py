from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Interest
from .constants import DEFAULT_INTERESTS
from .serializers import (
    InterestSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    LoginSerializer,
)


class InterestListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not Interest.objects.exists():
            Interest.objects.bulk_create(
                [Interest(name=name) for name in DEFAULT_INTERESTS],
                ignore_conflicts=True,
            )
        interests = Interest.objects.all().order_by('name')
        return Response(InterestSerializer(interests, many=True).data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'Registration successful.',
                'user': UserProfileSerializer(user.profile).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    def get(self, request):
        return Response(UserProfileSerializer(request.user.profile).data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
