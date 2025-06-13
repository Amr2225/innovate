from rest_framework.exceptions import APIException
from rest_framework import status


class MissingLectureError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "No lectures provided"
    error_type = "missing_lecture_id"


class InvalidLectureIdsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid lectures"
    error_type = "invalid_lecture_ids"


class InvalidMCQStructureError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid MCQ structure"
    error_type = "invalid_mcq_structure"


class InvalidMCQError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "MCQ question are required"
    error_type = "invalid_mcq"
