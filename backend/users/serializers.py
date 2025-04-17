from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.signing import TimestampSigner, Signer
import random
import uuid

from users.exceptions import EmailVerificationError
from users.validation import nationalId_length_validation

# Helpers
from .helper import generateOTP, sendEmail, generateTokens

# Errors
from .errors import EmailNotVerifiedError, UserAccountDisabledError, UserNotFoundError
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
            "institution_type",
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
            institution_type=validated_data['institution_type'],
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


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name")


class InstitutionUserSeralizer(serializers.ModelSerializer):
    # TODO: implement rules for the age attribute (calculated, or entered)
    Role = (
        ("Student", "Student"),
        ("Teacher", "Teacher"),
    )

    role = serializers.ChoiceField(choices=Role)
    institution = serializers.CharField(
        read_only=True, source="institution.id")

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "role",
            "national_id",
            "level",
            "semester",
            "birth_date",
            "age",
            "institution",
            "is_email_verified",
            "is_active",
            'date_joined',
            'email',
        )
        # extra_kwargs = {
        #     # "first_name": { 'required': True},
        #     # "middle_name": {'write_only': True, 'required': True},
        #     # "last_name": {'write_only': True, 'required': True},
        #     "role": {'write_only': True, 'required': True},
        #     "national_id": {'write_only': True, 'required': True},
        #     "birth_date": {'write_only': True, 'required': True},
        #     'date_joined': {'read_only': True},
        #     'is_email_verified': {'read_only': True},
        # }

    def create(self, data):
        request = self.context.get('request')
        user = User.objects.create(**data, access_code=None)
        user.save()
        user.institution.set([request.user])
        return user


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
            raise AuthenticationFailed()

        if not user.is_active:
            raise UserAccountDisabledError()

        if not user.is_email_verified:
            raise EmailNotVerifiedError()

        data['user'] = user
        return data

    def to_representation(self):
        errors = {}
        for field, error_list in self.errors.items():
            errors[field] = [str(error) for error in error_list]
        return errors


class LoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="JWT refresh token")
    access = serializers.CharField(help_text="JWT access token")


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text="Error message")


class FirstLoginSerializer(serializers.Serializer):
    access_code = serializers.CharField(max_length=8)
    national_id = serializers.CharField(max_length=14, validators=[
                                        nationalId_length_validation])

    def validate(self, data):
        access_code = data.get("access_code")
        national_id = data.get("national_id")

        if not access_code or not national_id:
            raise AuthenticationFailed(
                "Please provide both access code and national id")

        user = User.objects.get(national_id=national_id)

        if not user.institution.access_code == access_code:
            raise AuthenticationFailed(
                "Invalid institution Code or National ID")

        if not user.is_active:
            raise UserAccountDisabledError()

        if user.email and not user.is_email_verified:
            raise EmailVerificationError()

        data['user'] = user

        return data


class UserAddCredentialsSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "middle_name",
            "last_name",
            "email",
            'password',
            "confirm_password",
            'birth_date',
            'token',
        )
        extra_kwargs = {
            "first_name": {'write_only': True, 'required': True},
            "middle_name": {'write_only': True, 'required': True},
            "last_name": {'write_only': True, 'required': True},
            'email': {'write_only': True, 'required': True},
            'birth_date': {'write_only': True, 'required': True},
            'password': {'write_only': True, 'required': True},
            "confirm_password": {'write_only': True, 'required': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"message": "Passwords do not match."})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        # Remove the pop password from the validated_data
        validated_data.pop("confirm_password")

        user = User.objects.get(national_id=request.user.national_id)
        user.set_password(validated_data.get('password'))
        validated_data.pop("password")

        for key, value in validated_data.items():
            setattr(user, key, value)

        user.save()
        print(user)

        generateOTP(user)
        sendEmail(user.email, user.otp)

        signer = Signer()
        token = signer.sign(user.email)

        return {"token": token}
