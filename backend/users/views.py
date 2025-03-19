import random
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .serializers import ErrorResponseSerializer, InstitutionRegisterSeralizer, UserLoginSeralizer, LoginResponseSerializer

from django.core.signing import BadSignature, Signer

# Helpers
from .helper import sendEmail

# OTP Validation
from django.utils import timezone
from datetime import timedelta

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
User = get_user_model()


class InstitutionRegisterView(generics.CreateAPIView):
    model = User
    serializer_class = InstitutionRegisterSeralizer


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        signer = Signer()

        try:
            email = signer.unsign(token)
            user = User.objects.get(email=email)

            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Email already verified."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class ResendVerificationEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"message": "Invalid Email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if user.is_email_verified:
                return Response({"message": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

            # OTP is expired create a new one
            if user.otp_created_at + timedelta(minutes=user.otp_expiry_time_minutes) <= timezone.now():
                otp = str(random.randint(100000, 999999))
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()

            sendEmail(user.email, user.otp)

            return Response({"message": "Verification email resent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    allowed_methods = ["POST"]

    @extend_schema(
        request=UserLoginSeralizer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description="Login successful"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad request"
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized"
            ),
        },
        description="API endpoint for user login",
        summary="User login with JWT"
    )
    def post(self, request):
        try:
            serializer = UserLoginSeralizer(data=request.data)

            if serializer.is_valid():
                user = serializer.validated_data['user']

                # Generate tokens
                refresh = RefreshToken.for_user(user)

                if user.role == "Institution":
                    refresh['name'] = user.name
                    refresh['role'] = user.role
                    refresh['credits'] = user.credits
                    refresh['email'] = user.email
                else:
                    refresh['full_name'] = user.full_name
                    refresh['role'] = user.role

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)

        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
