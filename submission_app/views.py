from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import Any, Mapping

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import InvitationToken, User


class InviteRegisterSerializer(serializers.Serializer):
    token = serializers.CharField()
    name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class InviteRegisterView(APIView):
    """
    Register a user using an invitation token and return JWT tokens.
    """

    def post(self, request, *args, **kwargs):
        serializer = InviteRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data: Mapping[str, Any] = serializer.validated_data
        token_value = data["token"]
        name = data["name"]
        password = data["password"]

        try:
            invitation = InvitationToken.objects.select_for_update().get(token=token_value)
        except InvitationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid invitation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate token usage and expiry
        if invitation.used:
            return Response(
                {"detail": "This invitation token has already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.expiry_date <= timezone.now():
            return Response(
                {"detail": "This invitation token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserModel = get_user_model()

        with transaction.atomic():
            # Create user with email from token, role APPLICANT
            user = UserModel.objects.create_user(
                username=invitation.email,
                email=invitation.email,
                password=password,
            )
            # Ensure role is set to APPLICANT if the custom User model is used
            if isinstance(user, User):
                # Runtime assignment is valid; directive silences strict type-checker complaint
                user.role = User.Roles.APPLICANT  # pyright: ignore[reportAssignmentType]
               
                user.first_name = name
                user.save()

            # Mark token as used
            invitation.used = True
            invitation.save(update_fields=["used"])

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LoginView(APIView):
    """
    Standard login view that returns JWT tokens on successful authentication.
    """

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: Mapping[str, Any] = serializer.validated_data

        email = data["email"]
        password = data["password"]

        # Assuming email is used as the username field
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """
    Return basic profile information for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response(
            {
                "name": user.get_full_name() or user.first_name or user.username,
                "email": getattr(user, "email", ""),
                "is_finalized": getattr(user, "is_finalized", False),
            },
            status=status.HTTP_200_OK,
        )
