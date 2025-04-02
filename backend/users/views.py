from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .permissions import isInstitution
from .errors import EmailNotVerifiedError
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

from .serializers import ErrorResponseSerializer, FirstLoginSerializer, InstitutionRegisterSeralizer, InstitutionRegisterUserSeralizer, UserAddCredentialsSerializer, UserLoginSeralizer, LoginResponseSerializer
from .authentication import FirstLoginAuthentication

from rest_framework.parsers import MultiPartParser, FormParser

from google.oauth2 import id_token
from google.auth.transport import requests

from django.conf import settings
User = get_user_model()


class InstitutionRegisterView(generics.CreateAPIView):
    model = User
    serializer_class = InstitutionRegisterSeralizer


class BulkUserImportView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = InstitutionRegisterUserSeralizer

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
            io_string = io.StringIO(decoded_file)
            reader = list(csv.DictReader(io_string, delimiter=","))

            # Process each row from the dictionary
            for row in reader:
                print(row)
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
                else:
                    # Track errors for this row
                    errors.append({
                        'row': cleaned_row,
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


class InstitutionRegisterUserView(generics.CreateAPIView):
    model = User
    serializer_class = InstitutionRegisterUserSeralizer
    permission_classes = [isInstitution]


class VerifyEmailView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        email = request.data.get("email")

        # Validate Input
        if not email or not otp:
            return Response({"detail": "Invalid email or OTP"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            # Validate Email
            if user.is_email_verified:
                return Response({"detail": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate OTP
            if not user.otp == otp:
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
            if not user.otp_created_at or user.otp_created_at + timedelta(minutes=user.otp_expiry_time_minutes) <= timezone.now():
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
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except EmailNotVerifiedError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
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
