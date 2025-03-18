from django.shortcuts import render
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .models import User
from .serializers import UserSerializer, RegistrationSerializer, VerifyEmailSerializer, GoogleAuthSerializer
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.


class userListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Email verification helper function


def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user, code):
    """Send verification email with code."""
    subject = 'Verify your email address'
    message = f'Your verification code is: {code}. This code will expire in 10 minutes.'
    # from_email = settings.DEFAULT_FROM_EMAIL
    from_email = "asaid@dxperia.com"
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


class RegisterView(generics.CreateAPIView):
    """Register a new user and send verification code."""
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        # Generate and store verification code
        code = generate_verification_code()
        user.email_verification_code = code
        user.email_verification_code_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        # Send verification email
        send_verification_email(user, code)


class VerifyEmailView(views.APIView):
    """Verify email using the verification code."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if code is valid and not expired
        if (user.email_verification_code != code or
                user.email_verification_code_expiry < timezone.now()):
            return Response({'error': 'Invalid or expired verification code'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Activate user
        user.is_active = True
        user.is_valid = True
        user.email_verification_code = None
        user.email_verification_code_expiry = None
        user.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class ResendVerificationCodeView(views.APIView):
    """Resend verification code."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Generate and store new verification code
        code = generate_verification_code()
        user.email_verification_code = code
        user.email_verification_code_expiry = timezone.now() + timedelta(minutes=10)
        print("CODE", code)
        user.save()

        # Send verification email
        if send_verification_email(user, code):
            return Response({'message': 'Verification code sent'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send verification code'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleLoginView(SocialLoginView):
    """Handle Google OAuth2 authentication."""
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.WEBSITE_URL + "/auth/google/callback/"

    def get_response(self):
        response = super().get_response()

        # Check if user is new or existing based on the token
        if self.token:
            user = self.token.user

            # If this is a new user registration
            if not user.google_id:
                user.google_id = self.token.app.client_id
                user.is_active = True
                user.is_valid = True
                user.save()

        return response


class GoogleAuthView(views.APIView):
    """Handle Google authentication from frontend."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        google_id = serializer.validated_data['google_id']
        email = serializer.validated_data['email']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']

        # Get or create user
        try:
            user = User.objects.get(email=email)
            # Update Google ID if not already set
            if not user.google_id:
                user.google_id = google_id
                user.save()
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                google_id=google_id,
                is_active=True,
                is_valid=True,
                national_id="00000000000000"  # Placeholder for Google auth users
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
