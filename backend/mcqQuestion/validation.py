from rest_framework.exceptions import ValidationError
from decimal import Decimal
from .errors import InvalidMCQStructureError


def validate_difficulty(difficulty, DIFFICULTY_CHOICES):
    if difficulty is None:
        return '3'  # Default to Medium
    if difficulty not in [choice[0] for choice in DIFFICULTY_CHOICES]:
        raise ValidationError(
            "Invalid difficulty level. Must be one of: 1, 2, 3, 4, 5")
    return difficulty


def validate_num_options(num_options):
    try:
        # Default to 4 options
        num = int(num_options) if num_options is not None else 4
        if num < 2:
            raise ValidationError("Number of options must be at least 2")
        if num > 6:
            raise ValidationError("Maximum 6 options allowed per question")
        return num
    except (TypeError, ValueError):
        raise ValidationError("Number of options must be a valid integer")


def validate_num_questions(num_questions, default=10):
    try:
        num = int(num_questions) if num_questions is not None else default
        if num < 1:
            raise ValidationError("Number of questions must be positive")
        if num > 50:
            raise ValidationError(
                "Maximum 50 questions allowed per request")
        return num
    except (TypeError, ValueError):
        raise ValidationError(
            "Number of questions must be a valid integer")


# TODO: query for the assessment total grade


def validate_question_grade(question_grade):
    try:
        grade = Decimal(str(question_grade)
                        ) if question_grade is not None else Decimal('0.00')
        if grade < Decimal('0.00'):
            raise ValidationError("Question grade cannot be negative")
        if grade > Decimal('100.00'):
            raise ValidationError("Question grade cannot exceed 100")
        return grade
    except (TypeError, ValueError):
        raise ValidationError(
            "Question grade must be a valid decimal number")


def validate_mcq_structure(mcq):
    """Validate the structure of a single MCQ"""
    if not all(key in mcq for key in ['question', 'options', 'correct_answer', 'total_grade']):
        raise InvalidMCQStructureError(
            "Each MCQ must have question, options, correct answer, and total grade")

    if not isinstance(mcq['options'], list):
        raise InvalidMCQStructureError("Options must be a list")

    if len(mcq['options']) < 2:
        raise InvalidMCQStructureError("At least 2 options are required")

    if len(mcq['options']) > 6:
        raise InvalidMCQStructureError("Maximum 6 options allowed")

    if mcq['correct_answer'] not in mcq['options']:
        raise InvalidMCQStructureError(
            "Correct answer must be one of the options")
