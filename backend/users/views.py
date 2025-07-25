from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .permissions import isInstitution
from .errors import EmailNotVerifiedError, UserAccountDisabledError
from datetime import timedelta
from django.utils import timezone
import io
import csv
from .helper import generateTokens, sendEmail
import random
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.exceptions import EmailVerificationError

from .serializers import ErrorResponseSerializer, FirstLoginSerializer, InstitutionRegisterSeralizer, InstitutionUserSeralizer, UserAddCredentialsSerializer, UserLoginSeralizer, LoginResponseSerializer
from .authentication import FirstLoginAuthentication

from rest_framework.parsers import MultiPartParser, FormParser
from django.core.signing import Signer, BadSignature

from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.views import TokenRefreshView

from users.serializers import (ErrorResponseSerializer,
                               FirstLoginSerializer,
                               UserAddCredentialsSerializer,
                               UserLoginSeralizer,
                               LoginResponseSerializer,
                               CustomTokenRefreshSerializer,
                               UserUpdateSerializer,
                               ChangePasswordSerializer)

from institution_policy.models import InstitutionPolicy

from django.conf import settings
User = get_user_model()


class InstitutionRegisterView(generics.CreateAPIView):
    model = User
    serializer_class = InstitutionRegisterSeralizer


class BulkUserImportView(generics.CreateAPIView):
    permission_classes = [isInstitution]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = InstitutionUserSeralizer

    def create(self, request):
        csv_file = request.FILES.get('file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Please upload a valid CSV file'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Track results
        created_users = []
        errors = []

        # Process CSV file
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file, newline=None)
            reader = list(csv.DictReader(io_string, delimiter=","))

            # Process each row from the dictionary
            for row in reader:
                # Clean the data - strip whitespace and handle empty strings
                cleaned_row = {k: v.strip() if v else None for k,
                               v in row.items()}

                # Validate row data
                serializer = self.get_serializer(
                    data=cleaned_row, context={'request': request})

                if serializer.is_valid():
                    # Create user with institution relationship
                    self.perform_create(serializer)
                    created_users.append(serializer.data)
                    # instance = serializer.save()
                    # created_users.append(
                    #     InstitutionUserSeralizer(instance).data)
                else:
                    if 'national_id' in serializer.errors:
                        try:
                            existing_user = User.objects.exclude(
                                institution__in=[request.user]).get(national_id=serializer.data['national_id'])
                            # existing_user = User.objects.get(
                            #     national_id=serializer.data['national_id'])
                            existing_user.institution.add(request.user)
                            created_users.append(
                                self.get_serializer(existing_user).data)
                        except User.DoesNotExist:
                            print("user doesn't exist")
                            errors.append({
                                'row': serializer.data,
                                'errors': serializer.errors
                            })
                    else:
                        # existing_user = User.objects.filter(national_id=cleaned_row['national_id'])
                        # Track errors for this row
                        errors.append({
                            'row': serializer.data,
                            'errors': serializer.errors
                        })

            # Return results
            return Response({
                'success': True,
                'created_count': len(created_users),
                'created_users': created_users,
                'error_count': len(errors),
                'errors': errors
            }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class InstitutionUserView(generics.ListCreateAPIView):
    # model = User
    # queryset = User.objects.all()
    serializer_class = InstitutionUserSeralizer
    permission_classes = [isInstitution]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(institution=user)


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
                [access, refresh] = generateTokens(user)

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
        except EmailVerificationError as e:
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


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenRefreshSerializer


class UserUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the user
        user = self.get_object()

        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            "message": "Password updated successfully"
        }, status=status.HTTP_200_OK)
