# Django
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.signing import Signer

# DRF
from requests import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
# Refresh Token
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


# Models
from enrollments.models import Enrollments
from courses.models import Course
from lecture.models import Lecture, LectureProgress
from institution_policy.models import InstitutionPolicy

# Validation & Errors & Helpers
from users.errors import EmailNotVerifiedError, UserAccountDisabledError, NewPasswordMismatchError, OldPasswordIncorrectError, NewPasswordSameAsOldPasswordError
from users.validation import nationalId_length_validation
from users.helper import generateOTP, sendEmail

import random
from django.utils import timezone

# Python
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

        # Validate institution_type is required for role Institution
        if not data.get('institution_type'):
            raise serializers.ValidationError({
                'institution_type': 'This field is required for institutions.'
            })

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

        InstitutionPolicy.objects.create(institution=user)

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

    def create(self, data):
        request = self.context.get('request')
        user = User.objects.create(**data, access_code=None)
        user.save()
        user.institution.set([request.user])

        if data.get("role") == "Student":
            institution = request.user
            if getattr(institution, 'institution_type', None) == "school":
                matching_courses = Course.objects.filter(
                    semester=user.semester,
                    institution=institution
                )
                for course in matching_courses:
                    Enrollments.objects.create(user=user, course=course)
                    lectures = Lecture.objects.filter(chapter__course=course)
                    LectureProgress.objects.bulk_create([
                        LectureProgress(enrollment=Enrollments.objects.get(
                            user=user, course=course, is_completed=False), lecture=lecture)
                        for lecture in lectures
                    ])

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

        user = User.objects.get(national_id=national_id,
                                institution__access_code=access_code)

        if not user:
            raise AuthenticationFailed(
                "Invalid institution Code or National ID")

        if not user.is_active:
            raise UserAccountDisabledError()

        if user.email and not user.is_email_verified:
            raise EmailNotVerifiedError()

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


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Get the user from the refresh token
        refresh = RefreshToken(attrs['refresh'])
        user_id = refresh.get('user_id')
        user = User.objects.get(id=user_id)

        # Create new access token with updated claims
        new_access_token = RefreshToken.for_user(user)

        if user.role == "Institution":
            new_access_token['name'] = user.name
            new_access_token['credits'] = user.credits
            new_access_token['profile_picture'] = user.logo.url if user.logo else None
        else:
            new_access_token['name'] = user.full_name
            new_access_token['profile_picture'] = user.avatar.url if user.avatar else None

        new_access_token['role'] = user.role
        new_access_token['email'] = user.email

        # Update the access token in the response
        data['access'] = str(new_access_token.access_token)

        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'birth_date',
            'age',
            'national_id',
            'semester',
            'avatar',
            'name',
            'logo'
        ]
        read_only_fields = ['email']  # Email shouldn't be changeable

    def validate_national_id(self, value):
        if value:
            # Check if national_id is unique for the user's institution
            user = self.context['request'].user
            if User.objects.filter(
                national_id=value,
                institution=user.institution.first()
            ).exclude(id=user.id).exists():
                raise serializers.ValidationError(
                    "National ID already exists in your institution")
        return value

    def validate(self, data):
        # Add any cross-field validation here
        if 'birth_date' in data and 'age' in data:
            # You might want to validate that age matches birth_date
            pass
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise OldPasswordIncorrectError()
        return value

    def validate(self, data):
        user = self.context['request'].user

        # Check if new password is same as old password
        if user.check_password(data['new_password']):
            raise NewPasswordSameAsOldPasswordError()

        # Check if new password and confirm password match
        if data['new_password'] != data['confirm_password']:
            raise NewPasswordMismatchError()

        # Validate the new password
        try:
            validate_password(data['new_password'], user)
        except ValidationError as e:
            raise serializers.ValidationError({
                "new_password": list(e.messages)
            })

        return data
