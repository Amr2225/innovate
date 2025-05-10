# Django
from django.contrib.auth import get_user_model
from django.utils import timezone

# DRF
from rest_framework import serializers

# Python
import random

# Helpers
from users.helper import sendEmail

User = get_user_model()

# TODO: implement payment integration and fix this serializer


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
        read_only=True, source="institution.name")

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "role",
            "national_id",
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
