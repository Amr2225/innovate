from django.db import models
import uuid
from assessment.models import Assessment
from enrollments.models import Enrollments
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal
from django.conf import settings
import os
from django.core.files import File

class AssessmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    enrollment = models.ForeignKey(Enrollments, on_delete=models.CASCADE, related_name='assessment_submissions')
    mcq_answers = models.JSONField(default=dict, help_text="Dictionary of question_id: selected_answer")
    handwritten_answers = models.JSONField(default=dict, help_text="Dictionary of question_id: image_path")
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        app_label = 'AssessmentSubmission'
        unique_together = ('assessment', 'enrollment')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.assessment.title}"

    def save(self, *args, **kwargs):
        # First save the model
        super().save(*args, **kwargs)
        
        if self.is_submitted:
            try:
                # Validate all answers are present
                self.validate_answers()
                
                # Create MCQ scores
                self.create_mcq_scores()
                
                # Create Handwritten scores
                self.create_handwritten_scores()
                
                # Update assessment score
                self.update_assessment_score()
            except Exception as e:
                # If any error occurs during validation or score creation,
                # set is_submitted back to False and save again
                self.is_submitted = False
                super().save(*args, **kwargs)
                raise e

    def validate_answers(self):
        """Validate that all questions have been answered"""
        from mcqQuestion.models import McqQuestion
        from HandwrittenQuestion.models import HandwrittenQuestion
        from DynamicMCQ.models import DynamicMCQQuestions

        # Get all questions for the assessment
        mcq_questions = McqQuestion.objects.filter(
            assessment=self.assessment,
            created_by=self.enrollment.user
        )
        dynamic_mcq_questions = DynamicMCQQuestions.objects.filter(
            dynamic_mcq__assessment=self.assessment,
            created_by=self.enrollment.user
        )
        handwritten_questions = HandwrittenQuestion.objects.filter(
            assessment=self.assessment
        )

        # Check if there are any questions
        if not mcq_questions.exists() and not dynamic_mcq_questions.exists() and not handwritten_questions.exists():
            raise ValidationError("No questions found for this assessment")

        # Check MCQ answers
        for question in mcq_questions:
            if str(question.id) not in self.mcq_answers:
                raise ValidationError(f"Missing answer for MCQ question {question.id}")
            if self.mcq_answers[str(question.id)] not in question.options:
                raise ValidationError(f"Invalid answer for MCQ question {question.id}")

        # Check Dynamic MCQ answers
        for question in dynamic_mcq_questions:
            if str(question.id) not in self.mcq_answers:
                raise ValidationError(f"Missing answer for Dynamic MCQ question {question.id}")
            if self.mcq_answers[str(question.id)] not in question.options:
                raise ValidationError(f"Invalid answer for Dynamic MCQ question {question.id}")

        # Check Handwritten answers
        for question in handwritten_questions:
            if str(question.id) not in self.handwritten_answers:
                raise ValidationError(f"Missing answer for Handwritten question {question.id}")
            if not self.handwritten_answers[str(question.id)]:
                raise ValidationError(f"Invalid answer for Handwritten question {question.id}")

    def create_mcq_scores(self):
        """Create MCQQuestionScore records for each answer"""
        from MCQQuestionScore.models import MCQQuestionScore
        from mcqQuestion.models import McqQuestion
        from DynamicMCQ.models import DynamicMCQQuestions

        for question_id, selected_answer in self.mcq_answers.items():
            try:
                # Try to get regular MCQ question first
                try:
                    question = McqQuestion.objects.get(id=question_id)
                    is_dynamic = False
                except McqQuestion.DoesNotExist:
                    # If not found, try to get dynamic MCQ question
                    question = DynamicMCQQuestions.objects.get(
                        id=question_id,
                        dynamic_mcq__assessment=self.assessment,
                        created_by=self.enrollment.user
                    )
                    is_dynamic = True
                
                # Create or update score
                score_data = {
                    'enrollment': self.enrollment,
                    'selected_answer': selected_answer,
                    'is_correct': selected_answer == question.answer_key,
                    'score': question.question_grade if selected_answer == question.answer_key else 0
                }
                
                if is_dynamic:
                    score_data['dynamic_question'] = question
                else:
                    score_data['question'] = question
                
                MCQQuestionScore.objects.update_or_create(
                    question=question if not is_dynamic else None,
                    dynamic_question=question if is_dynamic else None,
                    enrollment=self.enrollment,
                    defaults=score_data
                )
            except (McqQuestion.DoesNotExist, DynamicMCQQuestions.DoesNotExist):
                raise ValidationError(f"Question {question_id} does not exist")
            except Exception as e:
                raise ValidationError(f"Error creating score for question {question_id}: {str(e)}")

    def create_handwritten_scores(self):
        """Create HandwrittenQuestionScore records for each answer"""
        from HandwrittenQuestion.models import HandwrittenQuestionScore, HandwrittenQuestion
        from main.AI import evaluate_handwritten_answer, extract_text_from_image

        for question_id, file_path in self.handwritten_answers.items():
            question = HandwrittenQuestion.objects.get(id=question_id)
            
            try:
                # Get the full path to the file
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                
                # Open the file
                with open(full_path, 'rb') as file_obj:
                    # Evaluate the answer using AI
                    score, feedback, extracted_text = evaluate_handwritten_answer(
                        question=question.question_text,
                        answer_key=question.answer_key,
                        student_answer_image=file_obj,
                        max_grade=float(question.max_grade)
                    )

                    # Create or update score
                    score_obj, created = HandwrittenQuestionScore.objects.update_or_create(
                        question=question,
                        enrollment=self.enrollment,
                        defaults={
                            'score': score,
                            'feedback': feedback,
                            'extracted_text': extracted_text
                        }
                    )

                    # Save the file using Django's file handling
                    with open(full_path, 'rb') as f:
                        score_obj.answer_image.save(
                            os.path.basename(file_path),
                            File(f),
                            save=True
                        )

            except Exception as e:
                raise ValidationError(f"Error evaluating handwritten answer: {str(e)}")

    def update_assessment_score(self):
        """Update the AssessmentScore with total score"""
        from assessment.models import AssessmentScore

        assessment_score, created = AssessmentScore.objects.get_or_create(
            enrollment=self.enrollment,
            assessment=self.assessment,
            defaults={'total_score': 0}
        )
        
        # The AssessmentScore's save method will automatically calculate the total score
        assessment_score.save()

    @classmethod
    def get_or_create_submission(cls, assessment, enrollment):
        """Get existing submission or create a new one"""
        submission, created = cls.objects.get_or_create(
            assessment=assessment,
            enrollment=enrollment,
            defaults={
                'mcq_answers': {},
                'handwritten_answers': {},
                'is_submitted': False
            }
        )
        return submission
