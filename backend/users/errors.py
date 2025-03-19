from rest_framework.exceptions import APIException
from rest_framework import status


class EmailNotVerifiedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Email not verified. Please verify your email address."
