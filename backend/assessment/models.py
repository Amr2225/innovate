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
from django.apps import apps

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

        # Validate that the sum of all assessment grades doesn't exceed course total_grade
        if self.course.total_grade is not None:
            # Get sum of grades for all assessments in this course
            total_assessment_grade = Assessment.objects.filter(
                course=self.course
            ).exclude(
                id=self.id  # Exclude current assessment when updating
            ).aggregate(
                total=Sum('grade')
            )['total'] or 0

            # Add current assessment grade
            total_assessment_grade += self.grade

            # Check if total exceeds course grade
            if total_assessment_grade > self.course.total_grade:
                raise ValidationError(
                    f"Total assessment grade ({total_assessment_grade}) exceeds course total grade ({self.course.total_grade})"
                )

        # Validate that assessment grade matches total question grades
        if self.pk:  # Only check for existing assessments
            total_question_grade = self.total_grade
            if total_question_grade > self.grade:
                raise ValidationError(
                    f"Total question grade ({total_question_grade}) exceeds assessment grade ({self.grade})"
                )

        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.accepting_submissions and self.due_date > timezone.now()

    @property
    def total_questions(self):
        return self.mcq_questions.count() + self.handwritten_questions.count()

    @property
    def total_grade(self):
        """
        Calculate total grade from all question types
        """
        # Get regular MCQ questions total
        mcq_total = self.mcq_questions.aggregate(total=Sum('question_grade'))['total'] or 0
        
        # Get dynamic MCQ questions total
        DynamicMCQQuestions = apps.get_model('DynamicMCQ', 'DynamicMCQQuestions')
        dynamic_mcq_total = DynamicMCQQuestions.objects.filter(
            dynamic_mcq__assessment=self
        ).aggregate(total=Sum('question_grade'))['total'] or 0
        
        # Get handwritten questions total
        handwritten_total = self.handwritten_questions.aggregate(total=Sum('max_grade'))['total'] or 0
        
        return mcq_total + dynamic_mcq_total + handwritten_total

    def get_student_score(self, student):
        """
        Calculate total score for a student based on their MCQQuestionScores
        """
        MCQQuestionScore = apps.get_model('MCQQuestionScore', 'MCQQuestionScore')
        
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
        DynamicMCQ = apps.get_model('DynamicMCQ', 'DynamicMCQ')
        DynamicMCQQuestions = apps.get_model('DynamicMCQ', 'DynamicMCQQuestions')
        McqQuestion = apps.get_model('mcqQuestion', 'McqQuestion')
        HandwrittenQuestion = apps.get_model('HandwrittenQuestion', 'HandwrittenQuestion')
        Lecture = apps.get_model('lecture', 'Lecture')
        from main.AI import generate_mcqs_from_multiple_pdfs

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
                    # Get lectures and their attachments
                    lectures = Lecture.objects.filter(
                        id__in=dynamic_mcq.lecture_ids,
                        attachment__isnull=False
                    )

                    if not lectures.exists():
                        raise ValidationError("No lectures with attachments found for this course")

                    # Get all PDF attachments
                    pdf_files = []
                    for lecture in lectures:
                        if lecture.attachment and lecture.attachment.name.endswith('.pdf'):
                            pdf_files.append(lecture.attachment)
                    
                    if not pdf_files:
                        raise ValidationError("No PDF attachments found in lectures")

                    # Generate questions using AI from PDFs with specified difficulty
                    generated_questions = generate_mcqs_from_multiple_pdfs(
                        pdf_files=pdf_files,
                        num_questions_per_pdf=dynamic_mcq.number_of_questions // len(pdf_files),  # Distribute questions evenly
                        difficulty=dynamic_mcq.difficulty  # Pass the difficulty from DynamicMCQ model
                    )
                    
                    # Create questions for this student
                    for q in generated_questions:
                        question = DynamicMCQQuestions.objects.create(
                            dynamic_mcq=dynamic_mcq,
                            question=q['question'],
                            options=q['options'],
                            answer_key=q['correct_answer'],
                            question_grade=dynamic_mcq.total_grade / dynamic_mcq.number_of_questions,
                            created_by=student,
                            difficulty=dynamic_mcq.difficulty  # Store the difficulty level
                        )
                        questions['dynamic_mcq'].append({
                            'id': str(question.id),
                            'question': question.question,
                            'options': question.options,
                            'grade': question.question_grade,
                            'section_number': dynamic_mcq.section_number,
                            'difficulty': question.difficulty  # Include difficulty in response
                        })
                else:
                    # Return existing questions
                    for question in dynamic_questions:
                        questions['dynamic_mcq'].append({
                            'id': str(question.id),
                            'question': question.question,
                            'options': question.options,
                            'grade': question.question_grade,
                            'section_number': dynamic_mcq.section_number,
                            'difficulty': question.difficulty  # Include difficulty in response
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
                    'grade': question.question_grade,
                    'section_number': question.section_number
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
                    'max_grade': question.max_grade,
                    'section_number': question.section_number
                })
        except Exception as e:
            print(f"Error getting handwritten questions: {str(e)}")

        return questions

    def generate_dynamic_questions(self, student):
        """
        Generate dynamic MCQ questions for a specific student using lecture attachments
        """
        if self.type != 'Dynamic_MCQ':
            return None

        from main.AI import generate_mcqs_from_multiple_pdfs
        McqQuestion = apps.get_model('mcqQuestion', 'McqQuestion')
        Enrollments = apps.get_model('enrollments', 'Enrollments')
        Lecture = apps.get_model('lecture', 'Lecture')

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

            # Get lectures and their attachments
            lectures = Lecture.objects.filter(
                course=self.course,
                attachment__isnull=False
            ).exclude(attachment='')

            if not lectures.exists():
                raise ValidationError("No lectures with attachments found for this course")

            # Get all PDF attachments
            pdf_files = [lecture.attachment for lecture in lectures if lecture.attachment.name.endswith('.pdf')]
            
            if not pdf_files:
                raise ValidationError("No PDF attachments found in lectures")

            # Generate questions using AI
            questions = generate_mcqs_from_multiple_pdfs(
                pdf_files=pdf_files,
                num_questions_per_pdf=self.number_of_questions // len(pdf_files)  # Distribute questions evenly
            )

            # Create questions for this student
            created_questions = []
            for q in questions:
                question = McqQuestion.objects.create(
                    assessment=self,
                    question=q['question'],
                    options=q['options'],
                    answer_key=q['correct_answer'],
                    created_by=student,
                    question_grade=self.grade / len(questions)  # Distribute grade evenly
                )
                created_questions.append(question)

            return created_questions

        except Exception as e:
            print(f"Error generating dynamic questions: {str(e)}")
            return None

    def validate_question_grade(self, new_question_grade, existing_question_id=None):
        """
        Validate that the total grade of all questions doesn't exceed the assessment grade
        """
        # Get current total grade excluding the question being updated
        current_total = 0
        
        # Get regular MCQ questions total
        mcq_total = self.mcq_questions.aggregate(total=Sum('question_grade'))['total'] or 0
        current_total += mcq_total
        
        # Get dynamic MCQ questions total
        DynamicMCQQuestions = apps.get_model('DynamicMCQ', 'DynamicMCQQuestions')
        dynamic_mcq_total = DynamicMCQQuestions.objects.filter(
            dynamic_mcq__assessment=self
        ).aggregate(total=Sum('question_grade'))['total'] or 0
        current_total += dynamic_mcq_total
        
        # Get handwritten questions total
        handwritten_total = self.handwritten_questions.aggregate(total=Sum('max_grade'))['total'] or 0
        current_total += handwritten_total
        
        # If updating an existing question, subtract its grade from the total
        if existing_question_id:
            try:
                # Try to find the question in each type
                try:
                    existing_question = self.mcq_questions.get(id=existing_question_id)
                    current_total -= existing_question.question_grade
                except self.mcq_questions.model.DoesNotExist:
                    try:
                        existing_question = DynamicMCQQuestions.objects.get(
                            id=existing_question_id,
                            dynamic_mcq__assessment=self
                        )
                        current_total -= existing_question.question_grade
                    except DynamicMCQQuestions.DoesNotExist:
                        try:
                            existing_question = self.handwritten_questions.get(id=existing_question_id)
                            current_total -= existing_question.max_grade
                        except self.handwritten_questions.model.DoesNotExist:
                            pass
            except Exception as e:
                print(f"Error finding existing question: {str(e)}")

        # Check if adding the new grade would exceed the assessment grade
        if current_total + new_question_grade > self.grade:
            raise ValidationError(
                f"Total grade of questions ({current_total + new_question_grade}) "
                f"exceeds assessment grade ({self.grade})"
            )

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
        return f"{self.assessment.title} - {self.enrollment.user.email}"

    def save(self, *args, **kwargs):
        # Calculate total score from MCQ and Handwritten scores
        MCQQuestionScore = apps.get_model('MCQQuestionScore', 'MCQQuestionScore')
        HandwrittenQuestionScore = apps.get_model('HandwrittenQuestion', 'HandwrittenQuestionScore')
        DynamicMCQQuestions = apps.get_model('DynamicMCQ', 'DynamicMCQQuestions')
        
        # Get regular MCQ scores
        mcq_score = MCQQuestionScore.objects.filter(
            question__assessment=self.assessment,
            enrollment=self.enrollment
        ).aggregate(total=Sum('score'))['total'] or 0
        
        # Get dynamic MCQ scores
        dynamic_mcq_score = MCQQuestionScore.objects.filter(
            dynamic_question__dynamic_mcq__assessment=self.assessment,
            enrollment=self.enrollment
        ).aggregate(total=Sum('score'))['total'] or 0
        
        # Get handwritten scores
        handwritten_score = HandwrittenQuestionScore.objects.filter(
            question__assessment=self.assessment,
            enrollment=self.enrollment
        ).aggregate(total=Sum('score'))['total'] or 0
        
        # Calculate total score
        self.total_score = mcq_score + dynamic_mcq_score + handwritten_score
        super().save(*args, **kwargs)

