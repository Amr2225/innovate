<<<<<<< HEAD
# Django
from django.core.signing import Signer, BadSignature
from django.contrib.auth import get_user_model

# DRF
=======
>>>>>>> c18b18b6528a743c9eafe47cb0522e151360994c
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
<<<<<<< HEAD
from rest_framework_simplejwt.authentication import JWTAuthentication
import jwt
=======
from django.core.signing import Signer, BadSignature
from django.contrib.auth import get_user_model
import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication
>>>>>>> c18b18b6528a743c9eafe47cb0522e151360994c

AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES


class FirstLoginAuthentication(BaseAuthentication):
    www_authenticate_realm = "api"
    media_type = "application/json"

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
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    # def authenticate_header(self, request):
    #     return 'Bearer'
