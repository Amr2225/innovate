from rest_framework.exceptions import APIException


class AIError(APIException):
    status_code = 400
    default_detail = "An error occurred while generating MCQs"
    default_code = "ai_error"
