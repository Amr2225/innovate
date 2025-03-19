import random
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.core.mail import send_mail
from django.utils import timezone

# Helpers
from .helper import generateVerificationLink, generateVerificationToken, sendEmail

User = get_user_model()


class InstitutionRegisterSeralizer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    detail = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "name",
            "credits",
            "email",
            "password",
            "confirm_password",
            "detail",
        )

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        # Creating User
        otp = str(random.randint(100000, 999999))
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            credits=validated_data['credits'],
            role="Institution",
            otp=otp,
            otp_created_at=timezone.now()
        )
        user.set_password(validated_data['password'])
        user.save()

        # Sending Email
        sendEmail(user.email, user.otp)

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['detail'] = "Verification email sent."
        return data


class UserLoginSeralizer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=30, write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise AuthenticationFailed(
                "Please provide both email and password")

        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled")

        if not user.is_email_verified:
            raise AuthenticationFailed("Email is not verified")

        data['user'] = user
        return data


class LoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="JWT refresh token")
    access = serializers.CharField(help_text="JWT access token")
    # user = serializers.DictField(help_text="User information")


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text="Error message")
