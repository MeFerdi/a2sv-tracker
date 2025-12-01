from rest_framework import serializers
from .models import InvitationToken


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

