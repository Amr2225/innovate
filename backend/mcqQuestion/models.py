from django.db import models
from assessment.models import Assessment
from users.models import User
import uuid

class McqQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=1000)  # Changed from question_text to question
    points = models.PositiveSmallIntegerField(default=1)  # Points for correct answer
    
    # Store choices as JSON array: [{"key": "A", "text": "Choice text"}, ...]
    answer = models.JSONField()  # Changed from choices to answer
    answer_key = models.CharField(max_length=255)  # Changed from correct_answer to answer_key
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mcq_questions_created')
    is_ai_generated = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.question[:50]}..."

    def get_choice_text(self, choice_key):
        """Get the text for a specific choice key"""
        for choice in self.answer:  # Changed from self.choices to self.answer
            if choice['key'].upper() == choice_key.upper():
                return choice['text']
        return None

    def get_choices_count(self):
        """Get the number of choices"""
        return len(self.answer)  # Changed from self.choices to self.answer

    def check_answer(self, student_answer):
        """
        Check if the student's answer is correct
        Args:
            student_answer: The letter chosen by the student
        Returns:
            bool: True if the answer is correct, False otherwise
        """
        if not student_answer:
            return False
            
        # Convert both to uppercase for comparison
        student_choice = student_answer.upper()
        correct_choice = self.answer_key.upper()  # Changed from correct_answer to answer_key
        
        # Validate that student_choice is a valid option
        valid_keys = [choice['key'].upper() for choice in self.answer]  # Changed from self.choices to self.answer
        if student_choice not in valid_keys:
            return False
            
        return student_choice == correct_choice

    def clean(self):
        """Validate the model data"""
        from django.core.exceptions import ValidationError
        
        # Validate choices format
        if not isinstance(self.answer, list):  # Changed from self.choices to self.answer
            raise ValidationError("Choices must be a list")
        
        # Check if choices is not empty
        if not self.answer:  # Changed from self.choices to self.answer
            raise ValidationError("Must provide at least one choice")
            
        # Validate each choice has required format
        valid_keys = []
        for i, choice in enumerate(self.answer):  # Changed from self.choices to self.answer
            if not isinstance(choice, dict):
                raise ValidationError(f"Choice {i} must be a dictionary")
            if 'key' not in choice or 'text' not in choice:
                raise ValidationError(f"Choice {i} must have 'key' and 'text' fields")
            valid_keys.append(choice['key'].upper())
            
        # Check for duplicate keys
        if len(valid_keys) != len(set(valid_keys)):
            raise ValidationError("Choice keys must be unique")
            
        # Validate correct_answer is one of the choice keys
        if self.answer_key.upper() not in valid_keys:  # Changed from correct_answer to answer_key
            raise ValidationError("Correct answer must be one of the choice keys")
