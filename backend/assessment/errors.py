from rest_framework.exceptions import APIException


class AssessmentInvalidDueDate(APIException):
    status_code = 400
    default_detail = "Due date must be in the future"
    error_type = "invalid_due_date"
