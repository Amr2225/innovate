from rest_framework.exceptions import APIException
from rest_framework import status


class UserNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Invalid credentials."


class EmailNotVerifiedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Email not verified, Please verify your email address."


class UserAccountDisabledError(APIException):
    status_code = status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
    default_detail = "User account is disabled."


class OldPasswordIncorrectError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Old password is incorrect."


class NewPasswordMismatchError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "New passwords don't match."


class NewPasswordSameAsOldPasswordError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "New password cannot be the same as the old password."
