# Djagno
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

# DRF
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

# Schema
from drf_spectacular.utils import extend_schema, OpenApiResponse


# Errors
from users.errors import EmailNotVerifiedError, UserAccountDisabledError

# Helpers
from users.helper import generateTokens

# Serializers
from users.serializers import (ErrorResponseSerializer,
                               FirstLoginSerializer,
                               UserAddCredentialsSerializer,
                               UserLoginSeralizer,
                               LoginResponseSerializer)

# Authentication
from users.authentication import FirstLoginAuthentication

# Google
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()


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
            serializer.is_valid(raise_exception=True)

            if serializer.is_valid():
                user = serializer.validated_data['user']

                # Generate tokens
                [refresh, access] = generateTokens(user)

                return Response({
                    'refresh': refresh,
                    'access': access,
                }, status=status.HTTP_200_OK)

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except EmailNotVerifiedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except UserAccountDisabledError as e:
            return Response({'error': str(e)}, status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class LoginAccessView(APIView):
    permission_classes = [AllowAny]
    allowed_methods = ["POST"]

    def post(self, request):
        try:
            serializer = FirstLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data['user']

            # Generate token
            [access, _] = generateTokens(user)

            return Response({'access': access, }, status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except EmailNotVerifiedError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except UserAccountDisabledError as e:
            return Response({'error': str(e)}, status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class UserAddCredentialsView(generics.CreateAPIView):
    authentication_classes = [FirstLoginAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddCredentialsSerializer
    allowed_methods = ["POST"]

    # def post(self, request):
    #     return JsonResponse({"Message": "message"})


class GoogleAuthView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            # Verify the Google token
            id_info = id_token.verify_oauth2_token(
                request.data.get('id_token'),
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return Response({'error': 'Wrong issuer.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create user
            email = id_info['email']

            # Created is just a boolean value to check if the user was created or not
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': id_info.get('given_name', ''),
                    'last_name': id_info.get('family_name', ''),
                }
            )

            print("USER", user)
            print("created", created)
            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role
            refresh['email'] = user.email

            # Create or get token
            # token, _ = user.objects.get_or_create(user=user)

            return Response({
                "refresh": str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'role': user.role
                }
            })
        except ValueError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
