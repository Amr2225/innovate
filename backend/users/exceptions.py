from rest_framework.exceptions import APIException
from rest_framework import status


class EmailVerificationError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Email verification failed"
    default_code = "email_verification_failed"
