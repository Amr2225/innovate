import uuid
from django.db import models
from users.models import User
from courses.models import Course
from django.utils import timezone
from django.db.models import Sum
from enrollments.models import Enrollments
from decimal import Decimal
import json
from django.core.exceptions import ValidationError

class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=255)
    type = models.CharField(
        max_length=50, 
        choices=[
            ('Exam', 'Exam'), 
            ('Assignment', 'Assignment'), 
            ('Quiz', 'Quiz')
        ]
    )
    due_date = models.DateTimeField()
    grade = models.PositiveSmallIntegerField()
    start_date = models.DateTimeField(default=timezone.now)
    accepting_submissions = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.course.name}"

    def save(self, *args, **kwargs):
        # Check if due date has passed
        if self.due_date < timezone.now():
            self.accepting_submissions = False
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.accepting_submissions and self.due_date > timezone.now()

    @property
    def total_questions(self):
        return self.mcq_questions.count() + self.handwritten_questions.count()

    @property
    def total_grade(self):
        mcq_total = self.mcq_questions.aggregate(total=Sum('question_grade'))['total'] or 0
        handwritten_total = self.handwritten_questions.aggregate(total=Sum('max_grade'))['total'] or 0
        return mcq_total + handwritten_total

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

    def get_all_questions_for_student(self, student):
        """
        Get all questions for a specific student from:
        1. DynamicMCQ app - Get or generate questions for the student
        2. MCQQuestion app - Get all MCQ questions
        3. HandwrittenQuestion app - Get all handwritten questions
        """
        from DynamicMCQ.models import DynamicMCQ, DynamicMCQQuestions
        from mcqQuestion.models import McqQuestion
        from HandwrittenQuestion.models import HandwrittenQuestion
        from main.AI import generate_mcq_questions

        questions = {
            'dynamic_mcq': [],
            'mcq': [],
            'handwritten': []
        }

        # 1. Get Dynamic MCQ Questions
        try:
            # Check if there's a DynamicMCQ entry for this assessment
            dynamic_mcq = DynamicMCQ.objects.filter(assessment=self).first()
            
            if dynamic_mcq:
                # Get existing questions for this student
                dynamic_questions = DynamicMCQQuestions.objects.filter(
                    dynamic_mcq=dynamic_mcq,
                    created_by=student
                )
                
                if not dynamic_questions.exists():
                    # Generate new questions if none exist
                    generated_questions = generate_mcq_questions(
                        context=dynamic_mcq.context,
                        num_questions=dynamic_mcq.number_of_questions,
                        difficulty=dynamic_mcq.difficulty
                    )
                    
                    # Create questions for this student
                    for q in generated_questions:
                        question = DynamicMCQQuestions.objects.create(
                            dynamic_mcq=dynamic_mcq,
                            question_text=q['question'],
                            options=q['options'],
                            correct_answer=q['correct_answer'],
                            created_by=student
                        )
                        questions['dynamic_mcq'].append({
                            'id': str(question.id),
                            'question': question.question_text,
                            'options': question.options,
                            'difficulty': question.difficulty
                        })
                else:
                    # Return existing questions
                    for question in dynamic_questions:
                        questions['dynamic_mcq'].append({
                            'id': str(question.id),
                            'question': question.question_text,
                            'options': question.options,
                            'difficulty': question.difficulty
                        })
        except Exception as e:
            print(f"Error getting dynamic MCQ questions: {str(e)}")

        # 2. Get Regular MCQ Questions
        try:
            mcq_questions = McqQuestion.objects.filter(assessment=self)
            for question in mcq_questions:
                questions['mcq'].append({
                    'id': str(question.id),
                    'question': question.question,
                    'options': question.options,
                    'grade': question.question_grade
                })
        except Exception as e:
            print(f"Error getting MCQ questions: {str(e)}")

        # 3. Get Handwritten Questions
        try:
            handwritten_questions = HandwrittenQuestion.objects.filter(assessment=self)
            for question in handwritten_questions:
                questions['handwritten'].append({
                    'id': str(question.id),
                    'question': question.question_text,
                    'max_grade': question.max_grade
                })
        except Exception as e:
            print(f"Error getting handwritten questions: {str(e)}")

        return questions

    def generate_dynamic_questions(self, student):
        """
        Generate dynamic MCQ questions for a specific student
        """
        if self.type != 'Dynamic_MCQ':
            return None

        from main.AI import generate_mcq_questions
        from mcqQuestion.models import McqQuestion
        from enrollments.models import Enrollments

        try:
            # Get student's enrollment
            enrollment = Enrollments.objects.get(user=student, course=self.course)
            
            # Check if questions already exist for this student
            existing_questions = McqQuestion.objects.filter(
                assessment=self,
                created_by=student
            )
            if existing_questions.exists():
                return existing_questions

            # Get context from file or text
            context = ""
            if self.context_file:
                # Read PDF or text file
                import PyPDF2
                if self.context_file.name.endswith('.pdf'):
                    with self.context_file.open('rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            context += page.extract_text()
                else:
                    context = self.context_file.read().decode('utf-8')
            else:
                context = self.context_text

            # Generate questions using AI
            questions = generate_mcq_questions(
                context=context,
                num_questions=self.number_of_questions,
                difficulty=self.difficulty_level
            )

            # Create MCQ questions for this student
            created_questions = []
            for q in questions:
                question = McqQuestion.objects.create(
                    assessment=self,
                    question=q['question'],
                    options=q['options'],
                    answer_key=q['correct_answer'],
                    question_grade=self.grade / self.number_of_questions,
                    created_by=student  # Track who generated the questions
                )
                created_questions.append(question)

            return created_questions

        except Exception as e:
            raise ValidationError(f"Error generating dynamic questions: {str(e)}")
    
class AssessmentScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scores')
    enrollment = models.ForeignKey(Enrollments, on_delete=models.CASCADE, related_name='assessment_scores')
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assessment', 'enrollment')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.assessment.title}"

    def save(self, *args, **kwargs):
        # Calculate total score from MCQ and Handwritten scores
        mcq_total = self.enrollment.mcq_question_scores.filter(
            question__assessment=self.assessment
        ).aggregate(total=Sum('score'))['total'] or 0

        handwritten_total = self.enrollment.handwritten_question_scores.filter(
            question__assessment=self.assessment
        ).aggregate(total=Sum('score'))['total'] or 0

        self.total_score = Decimal(str(mcq_total)) + Decimal(str(handwritten_total))
        super().save(*args, **kwargs)

