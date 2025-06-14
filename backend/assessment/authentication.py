import jwt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class EventStreamAuthentication(JWTAuthentication):
    www_authenticate_realm = "api"
    media_type = "text/event-stream"

    def authenticate(self, token):
        print(token)
        if token is None:
            return None

        try:
            validated_token = self.get_validated_token(token)
            print(validated_token)

            user = self.get_user(validated_token)
            print("USER", user)

            if user is None:
                raise AuthenticationFailed('User not found')

            return user
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None
