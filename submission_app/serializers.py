from django.utils import timezone
from rest_framework import serializers
from .models import InvitationToken, User


class InvitationTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for InvitationToken model, excluding sensitive fields.
    """

    class Meta:
        model = InvitationToken
        fields = ['id', 'email', 'used', 'expiry_date']
        read_only_fields = ['id', 'used']


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for token-based registration.
    """

    token = serializers.CharField()
    name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate_token(self, value):
        """
        Validate that the token exists, is not used, and is not expired.
        """
        try:
            invitation = InvitationToken.objects.get(token=value)
        except InvitationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token.")
        
        if invitation.used:
            raise serializers.ValidationError("This invitation token has already been used.")
        
        if invitation.expiry_date <= timezone.now():
            raise serializers.ValidationError("This invitation token has expired.")
        
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for User model profile information.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['name', 'email', 'role', 'is_finalized']
        read_only_fields = ['name', 'email', 'role', 'is_finalized']

    def get_name(self, obj):
        """Return the user's full name, first name, or username."""
        return obj.get_full_name() or obj.first_name or obj.username

