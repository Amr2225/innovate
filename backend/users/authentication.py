from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, ParseError
from django.core.signing import Signer, BadSignature
from django.contrib.auth import get_user_model

import os
import jwt


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Store the request object for use in token validation
        self.request = request
        return super().authenticate(request)

    def get_validated_token(self, raw_token):
        try:
            print("token", raw_token.decode('utf-8'))
            token = raw_token.decode('utf-8')

            return self.validate_token(token, "secret-secret-secret")
            # Determine the signing key based on the request path
            tokenNumber = self.request.query_params.get('token')
            if tokenNumber and int(tokenNumber) == 1:
                api_settings.SIGNING_KEY = os.environ.get('JWT_ACCESS_LOGIN')
                # self.validate_token(raw_token, os.environ.get("JWT_ACCESS_LOGIN"))
                print(api_settings.SIGNING_KEY)
                print("JWT SECOND")
            else:
                api_settings.SIGNING_KEY = os.environ.get('JWT_MAIN')
                print(api_settings.SIGNING_KEY)
                print("JWT MAIN")

            # Validate the token using the appropriate key
            # return super().get_validated_token(raw_token)
        except Exception as e:
            print(e)
            raise InvalidToken('Invalid token')

    def validate_token(self, token, signing_key):
        """Validate token with a specific signing key"""
        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=api_settings.ALGORITHM
            )
        except jwt.InvalidTokenError as e:
            raise InvalidToken(str(e))

        # Additional validation logic can go here
        return payload


class FirstLoginAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if jwt_token is None:
            return None

        jwt_token = self.getTokenFromHeader(jwt_token)  # clean the token

        try:
            payload = jwt.decode(
                jwt_token, api_settings.SIGNING_KEY, algorithms=api_settings.ALGORITHM)

            singer = Signer()
            national_id = singer.unsign(payload.get('national_id', ""))

            if not national_id:
                raise InvalidToken()

        except jwt.exceptions.InvalidSignatureError as e:
            raise InvalidToken()
        except jwt.exceptions.DecodeError as e:
            raise InvalidToken()
        except jwt.exceptions.ExpiredSignatureError as e:
            raise InvalidToken()
        except BadSignature:
            raise InvalidToken()

        User = get_user_model()

        user = User.objects.get(national_id=national_id)
        if user is None:
            raise AuthenticationFailed('User not found')

        return (user, None)

    def getTokenFromHeader(self, token):
        token = token.replace('Bearer', '').replace(' ', '')  # clean the token
        return token

    def authenticate_header(self, request):
        return 'Bearer'
