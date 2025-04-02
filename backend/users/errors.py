from rest_framework.exceptions import APIException
from rest_framework import status


class UserNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Invalid credentials"


class EmailNotVerifiedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Email not verified. Please verify your email address."


class UserAccountDisabledError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "User account is disabled."
