# Django
from django.contrib.auth import get_user_model
from django.core.cache import cache

# DRF
from rest_framework import serializers

# Python
import random

# Helpers
from users.helper import generateTokens
from .models import Payment

User = get_user_model()

# TODO: implement payment integration and fix this serializer


class InstitutionPaymentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ("name", "email", "credits")

    extra_kwargs = {
        "name": {"required": True},
        "email": {"required": True},
        "credits": {"required": True},
    }


class InstitutionRegisterSeralizer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    hmac = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "password",
            "confirm_password",
            "credits",
            "hmac",
            "access_token",
            "refresh_token",
        )

    def validate(self, data):
        print("invalid password")
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        # Get payment data from cache
        payment_data = cache.get(data['hmac'])
        if not payment_data:
            print("NO payment")
            raise serializers.ValidationError(
                "Invalid or expired payment session.")

        # Add payment data to validated data
        data['payment_data'] = payment_data
        return data

    def create(self, validated_data):
        payment_data = validated_data.pop('payment_data')
        hmac = validated_data.pop('hmac')

        # Creating Institution
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            credits=validated_data['credits'],
            role="Institution",
            is_email_verified=True,
            is_active=True,
        )
        user.set_password(validated_data['password'])

        # Creating Payment
        payment = Payment(
            institution=user,
            plan_id=payment_data['plan_id'],
            payment_status=payment_data['success'],
            transaction_id=payment_data['transaction_id'],
            order_id=payment_data['order_id'],
            credits_amount=user.credits,
        )

        user.save()
        payment.save()

        # Clear the cache
        cache.delete(hmac)

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        [accessToken, refreshToken] = generateTokens(instance)
        data['access_token'] = accessToken
        data['refresh_token'] = refreshToken
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
