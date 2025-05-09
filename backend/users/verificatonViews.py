# Django
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.signing import Signer, BadSignature
from django.core.cache import cache

# DRF
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Python
import random
from datetime import timedelta

# Helpers
from users.helper import sendEmail
User = get_user_model()


class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            signer = Signer()
            email = signer.unsign(token)

            user = User.objects.get(email=email)

            if not user:
                return Response({"message": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

            if user.is_email_verified:
                return Response({"detail": "Email is already verified"}, status=status.HTTP_403_FORBIDDEN)

        except BadSignature:
            return Response({"message": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_200_OK)

    def post(self, request, token):
        otp = request.data.get("otp")

        try:
            # Validate Input
            signer = Signer()
            email = signer.unsign(token)

            if not email or not otp:
                return Response({"detail": "Invalid email or OTP"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(email=email)
            # Validate Email
            if user.is_email_verified:
                return Response({"detail": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate OTP
            if not user.otp == str(otp):
                return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

            if user.otp_created_at + timedelta(minutes=user.otp_expiry_time_minutes) <= timezone.now():
                return Response({"detail": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Verify User
            user.is_email_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except BadSignature:
            return Response({"message": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)


class InstitutionResendVerificationEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")

        # Check if email is passed
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_403_FORBIDDEN)

        # Check if user with the email already exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user:
            return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP is already stored
        stored_otp = cache.get(email, None)
        if stored_otp:
            sendEmail(email, stored_otp)
            return Response({"message": "Verification email already resent"}, status=status.HTTP_200_OK)

        # Generate a new OTP
        otp = str(random.randint(100000, 999999))
        # timeout in seconds (60 seconds * 15 = 15 minutes)
        cache.set(email, otp, timeout=60 * 15)
        sendEmail(email, otp)

        return Response({"message": "Verification email sent"}, status=status.HTTP_200_OK)


class InstitutionVerifyEmail(APIView):
    def get(self, request, email):
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        found = cache.get(email, None)

        if not found:
            return Response({"message": "Email not found, please resend the verification email"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)

    def post(self, request, email=None):
        otp = request.data.get("otp")
        storedOTP = cache.get(email, None)

        if not storedOTP:
            return Response({"message": "Email not found, please resend the verification email"}, status=status.HTTP_404_NOT_FOUND)

        if not otp == int(storedOTP):
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if not email or not otp:
            return Response({"message": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(email)
        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    def post(self, request, token=None):
        email = request.data.get('email', None)

        try:
            if token:
                signer = Signer()
                email = signer.unsign(token)

            if not email:
                return Response({"message": "Invalid Email"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=email)
            if user.is_email_verified:
                return Response({"message": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

            # OTP is expired create a new one
            if not user.otp_created_at or user.otp_created_at + timedelta(minutes=user.otp_expiry_time_minutes) <= timezone.now():
                otp = str(random.randint(100000, 999999))
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()

            sendEmail(user.email, user.otp)

            if not token:
                signer = Signer()
                token = signer.sign(user.email)
                return Response({"message": "Verification email resent.", "token": token}, status=status.HTTP_200_OK)

            return Response({"message": "Verification email resent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except BadSignature:
            return Response({"message": "Invalid token"}, status=status.HTTP_403_FORBIDDEN)
