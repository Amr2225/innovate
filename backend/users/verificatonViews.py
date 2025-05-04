# Django
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.signing import Signer, BadSignature

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
        print(otp)

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
