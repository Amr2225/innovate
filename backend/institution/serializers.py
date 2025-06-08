# Django
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

# DRF
from rest_framework import serializers

# Python
import random

# Helpers
from users.helper import generateTokens
from .models import Payment

User = get_user_model()


class InstitutionGeneratePaymentSerializer(serializers.ModelSerializer):
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


class InstitutionBuyCreditsSerializer(serializers.ModelSerializer):
    hmac = serializers.CharField(write_only=True)

    class Meta:
        model = Payment
        fields = ['hmac']
        extra_kwargs = {
            "hmac": {"required": True},
        }

    def create(self, validated_data):
        data = cache.get(validated_data['hmac'])
        print("HMAC: ", validated_data['hmac'])
        print("Data: ", data)

        # Get the last payment for this institution
        last_payment = Payment.objects.filter(
            institution=self.context['request'].user,
            is_current=True
        ).first()

        # If there's a last payment, update its valid_to date and is_current status
        if last_payment:
            last_payment.valid_to = timezone.now()
            last_payment.is_current = False
            last_payment.save()

        # Create the new payment
        payment = Payment(
            institution=self.context['request'].user,
            plan_id=data['plan_id'],
            payment_status=data['success'],
            transaction_id=data['transaction_id'],
            order_id=data['order_id'],
            credits_amount=data['credits_amount'],
            is_current=True
        )
        payment.save()
        return payment


class InstitutionRegisterSeralizer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    hmac = serializers.CharField(write_only=True)
    logo = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True)

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "password",
            "confirm_password",
            "credits",
            "logo",
            "hmac",
            "access",
            "refresh",
        )

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            print("Passwords do not match")
            raise serializers.ValidationError("Passwords do not match.")

        # Get payment data from cache
        payment_data = cache.get(data['hmac'])
        if not payment_data:
            print("Payment Data Not Found")
            raise serializers.ValidationError(
                "Invalid or expired payment session.")

        # Add payment data to validated data
        data['payment_data'] = payment_data
        return data

    def validate_logo(self, value):
        if value:
            # Check file size (5MB limit)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "File size must be no more than 5MB")

            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "File type not supported. Please upload a JPEG, PNG, or GIF image.")
        return value

    def create(self, validated_data):
        payment_data = validated_data.pop('payment_data')
        hmac = validated_data.pop('hmac')
        print("CREDTIS FROM PAYMENT: ", validated_data['credits'])

        # Creating Institution
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            role="Institution",
            logo=validated_data['logo'],
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
            credits_amount=validated_data['credits'],
        )

        user.save()
        payment.save()

        # Clear the cache
        cache.delete(hmac)

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        [accessToken, refreshToken] = generateTokens(instance)
        data['access'] = accessToken
        data['refresh'] = refreshToken
        return data


class InstitutionUserSeralizer(serializers.ModelSerializer):
    # TODO: implement rules for the age attribute (calculated, or entered)
    Role = (
        ("Student", "Student"),
        ("Teacher", "Teacher"),
    )

    role = serializers.ChoiceField(choices=Role)
    institution = serializers.CharField(
        read_only=True, source="institution.name")

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.full_name

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
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
