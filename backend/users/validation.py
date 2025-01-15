from django.core.exceptions import ValidationError


def nationalId_length_validation(value):
    nationalId = value
    nationalIdString = str(nationalId)
    nationalIdLength = len(nationalIdString)
    if nationalIdLength < 14 or nationalIdLength > 14:
        raise ValidationError("Nationalid ID is invalid")
