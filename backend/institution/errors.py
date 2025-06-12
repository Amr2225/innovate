from rest_framework.exceptions import APIException


class InstitutionCreditError(APIException):
    status_code = 400
    default_detail = "Not enough credits to add a user."
    default_code = "institution_credit_error"


class InstitutionNationalIdError(APIException):
    status_code = 400
    default_detail = "A user with this national ID already exists in your institution "
    default_code = "institution_national_id_error"


class InstitutionEmailError(APIException):
    status_code = 400
    default_detail = "A user with this email already exists"
    default_code = "institution_email_error"
