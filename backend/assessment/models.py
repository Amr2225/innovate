import uuid
from django.db import models
from users.models import User
from courses.models import Course
from django.utils import timezone
from django.db.models import Sum
from enrollments.models import Enrollments
from decimal import Decimal
import json

class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=[('Exam', 'Exam'), ('Assignment', 'Assignment'), ('Quiz', 'Quiz')])
    due_date = models.DateTimeField()
    grade = models.PositiveSmallIntegerField()
    start_date = models.DateTimeField(default=timezone.now)
    accepting_submissions = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    @property
    def is_active(self):
        """
        Returns True if the assessment is currently active (between start and due date)
        """
        now = timezone.now()
        return self.start_date <= now <= self.due_date

    def get_student_score(self, student):
        """
        Calculate total score for a student based on their MCQQuestionScores
        """
        from MCQQuestionScore.models import MCQQuestionScore
        
        # Get the enrollment for this student and course
        enrollment = Enrollments.objects.get(user=student, course=self.course)
        
        return MCQQuestionScore.objects.filter(
            question__assessment=self,
            enrollment=enrollment
        ).aggregate(total=Sum('score'))['total'] or 0
    
class AssessmentScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey('enrollments.Enrollments', on_delete=models.CASCADE, related_name='assessment_scores')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scores')
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'assessment')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.assessment.title} - {self.total_score}"

    def save(self, *args, **kwargs):
        # Calculate total score from MCQQuestionScores
        from MCQQuestionScore.models import MCQQuestionScore
        mcq_total = MCQQuestionScore.objects.filter(
            question__assessment=self.assessment,
            enrollment=self.enrollment
        ).aggregate(total=Sum('score'))['total'] or Decimal('0')
        
        # Calculate total score from HandwrittenQuestionScores
        from HandwrittenQuestion.models import HandwrittenQuestionScore
        handwritten_total = HandwrittenQuestionScore.objects.filter(
            question__assessment=self.assessment,
            enrollment=self.enrollment
        ).aggregate(total=Sum('score'))['total'] or Decimal('0')
        
        # Set total score
        self.total_score = mcq_total + handwritten_total
        super().save(*args, **kwargs)

class AssessmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    enrollment = models.ForeignKey(Enrollments, on_delete=models.CASCADE, related_name='assessment_submissions')
    mcq_answers = models.JSONField(default=dict, help_text="Dictionary of question_id: selected_answer")
    handwritten_answers = models.JSONField(default=dict, help_text="Dictionary of question_id: image_path")
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('assessment', 'enrollment')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.assessment.title}"

    def save(self, *args, **kwargs):
        if self.is_submitted:
            # Validate all answers are present
            self.validate_answers()
            
            # Create MCQ scores
            self.create_mcq_scores()
            
            # Create Handwritten scores
            self.create_handwritten_scores()
            
            # Update assessment score
            self.update_assessment_score()
        
        super().save(*args, **kwargs)

    def validate_answers(self):
        """Validate that all questions have been answered"""
        from mcqQuestion.models import McqQuestion
        from HandwrittenQuestion.models import HandwrittenQuestion

        # Get all questions for the assessment
        mcq_questions = McqQuestion.objects.filter(assessment=self.assessment)
        handwritten_questions = HandwrittenQuestion.objects.filter(assessment=self.assessment)

        # Check MCQ answers
        for question in mcq_questions:
            if str(question.id) not in self.mcq_answers:
                raise ValidationError(f"Missing answer for MCQ question {question.id}")

        # Check Handwritten answers
        for question in handwritten_questions:
            if str(question.id) not in self.handwritten_answers:
                raise ValidationError(f"Missing answer for Handwritten question {question.id}")

    def create_mcq_scores(self):
        """Create MCQQuestionScore records for each answer"""
        from MCQQuestionScore.models import MCQQuestionScore
        from mcqQuestion.models import McqQuestion

        for question_id, selected_answer in self.mcq_answers.items():
            question = McqQuestion.objects.get(id=question_id)
            
            # Create or update score
            MCQQuestionScore.objects.update_or_create(
                question=question,
                enrollment=self.enrollment,
                defaults={
                    'selected_answer': selected_answer,
                    'is_correct': selected_answer == question.answer_key,
                    'score': question.question_grade if selected_answer == question.answer_key else 0
                }
            )

    def create_handwritten_scores(self):
        """Create HandwrittenQuestionScore records for each answer"""
        from HandwrittenQuestion.models import HandwrittenQuestionScore, HandwrittenQuestion
        from main.AI import evaluate_handwritten_answer, extract_text_from_image

        for question_id, image_path in self.handwritten_answers.items():
            question = HandwrittenQuestion.objects.get(id=question_id)
            
            try:
                # Evaluate the answer using AI
                score, feedback, extracted_text = evaluate_handwritten_answer(
                    question=question.question_text,
                    answer_key=question.answer_key,
                    student_answer_image=image_path,
                    max_grade=float(question.max_grade)
                )

                # Create or update score
                HandwrittenQuestionScore.objects.update_or_create(
                    question=question,
                    enrollment=self.enrollment,
                    defaults={
                        'score': score,
                        'feedback': feedback,
                        'answer_image': image_path,
                        'extracted_text': extracted_text
                    }
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

