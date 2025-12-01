from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import Any, Mapping

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import InvitationToken, User, Question, Submission


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


class ApplicantQuestionListView(APIView):
    """
    Return a list of all active questions, sorted by type and difficulty.
    Annotated with the authenticated user's submission status and link.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get all active questions, sorted by q_type then difficulty
        questions = Question.objects.filter(is_active=True).order_by(
            'q_type', 'difficulty'
        )
        
        # Prefetch user's submissions for these questions
        user_submissions = {
            sub.question_id: sub
            for sub in Submission.objects.filter(
                user=user,
                question__in=questions
            ).select_related('question')
        }
        
        # Build response data
        questions_data = []
        for question in questions:
            submission = user_submissions.get(question.id)
            questions_data.append({
                'id': question.id,
                'title': question.title,
                'leetcode_link': question.leetcode_link,
                'q_type': question.q_type,
                'difficulty': question.difficulty,
                'is_active': question.is_active,
                'submission': {
                    'submitted': submission is not None,
                    'submission_link': submission.submission_link if submission else None,
                    'submitted_at': submission.submitted_at.isoformat() if submission else None,
                } if submission else {
                    'submitted': False,
                    'submission_link': None,
                    'submitted_at': None,
                },
            })
        
        return Response(questions_data, status=status.HTTP_200_OK)


class FinalizeApplicationView(APIView):
    """
    Finalize the user's application if they have submitted 15 mandatory questions.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Count submissions for MANDATORY questions
        mandatory_submission_count = Submission.objects.filter(
            user=user,
            question__q_type=Question.QuestionType.MANDATORY
        ).count()
        
        # Check if requirement is met
        if mandatory_submission_count != 15:
            return Response(
                {
                    "detail": f"Application cannot be finalized. You have submitted {mandatory_submission_count} mandatory questions. 15 mandatory submissions are required.",
                    "mandatory_submission_count": mandatory_submission_count,
                    "required_count": 15,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Set is_finalized to True
        if isinstance(user, User):
            user.is_finalized = True
            user.save(update_fields=["is_finalized"])
        
        return Response(
            {
                "detail": "Application finalized successfully.",
                "is_finalized": True,
            },
            status=status.HTTP_200_OK,
        )


class IsAdminUser(BasePermission):
    """
    Custom permission to only allow users with role='ADMIN' to access the view.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has ADMIN role
        if isinstance(request.user, User):
            return request.user.role == User.Roles.ADMIN
        
        return False


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model.
    """

    class Meta:
        model = Question
        fields = ['id', 'title', 'leetcode_link', 'q_type', 'difficulty', 'is_active']


class QuestionAdminViewSet(ModelViewSet):
    """
    ViewSet for managing Question objects. Only accessible by ADMIN users.
    Implements soft-deletion by setting is_active=False instead of deleting.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        """
        Soft-delete: Set is_active=False instead of actually deleting the question.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        
        return Response(
            {"detail": "Question deactivated successfully."},
            status=status.HTTP_200_OK,
        )
