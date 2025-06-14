from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal
from django.db import models
import logging

# Import models
from users.models import User
from courses.models import Course
from chapter.models import Chapter
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore
from mcqQuestion.models import McqQuestion
from MCQQuestionScore.models import MCQQuestionScore
from HandwrittenQuestion.models import HandwrittenQuestion, HandwrittenQuestionScore
from enrollments.models import Enrollments

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **options):
        """Main function to populate the database with test data."""
        try:
            logger.info("Starting data population...")

            logger.info("Creating users...")
            institution, teachers, students = self.create_users()

            logger.info("Creating courses...")
            courses = self.create_courses(institution, teachers)

            logger.info("Creating enrollments...")
            enrollments = self.create_enrollments(courses, students)

            logger.info("Creating chapters...")
            chapters = self.create_chapters(courses)

            logger.info("Creating lectures...")
            lectures = self.create_lectures(chapters)

            logger.info("Creating lecture progress...")
            self.create_lecture_progress(lectures, enrollments)

            logger.info("Creating assessments...")
            assessments = self.create_assessments(courses)

            logger.info("Creating MCQ questions...")
            mcq_questions = self.create_mcq_questions(assessments, teachers)

            logger.info("Creating Handwritten questions...")
            handwritten_questions = self.create_handwritten_questions(
                assessments, teachers)

            logger.info("Creating MCQ scores...")
            self.create_mcq_scores(mcq_questions, enrollments)

            logger.info("Creating Handwritten scores...")
            self.create_handwritten_scores(handwritten_questions, enrollments)

            logger.info("Creating Assessment scores...")
            self.create_assessment_scores(assessments, enrollments)

            logger.info("Data population completed successfully!")
            self.stdout.write(self.style.SUCCESS(
                'Successfully populated database with test data'))
        except Exception as e:
            logger.error(f"Error in main function: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise

    def create_users(self):
        """Create test users including institution, teachers, and students."""
        try:
            # Create Institution
            institution = User.objects.create(
                email='institution@test.com',
                password='testpass123',
                role='Institution',
                institution_type='FACULTY',
                name='Test University',
                credits=100,
                is_email_verified=True,
                is_active=True
            )
            institution.set_password('testpass123')
            institution.save()
            logger.info(f"Created institution: {institution.name}")

            # Create Teachers
            teachers = []
            for i in range(3):
                teacher = User.objects.create(
                    email=f'teacher{i}@test.com',
                    password='testpass123',
                    role='Teacher',
                    first_name=f'Teacher{i}',
                    last_name=f'Last{i}',
                    is_email_verified=True,
                    is_active=True
                )
                teacher.set_password('testpass123')
                teacher.save()
                teachers.append(teacher)
                logger.info(f"Created teacher: {teacher.email}")

            # Create Students
            students = []
            for i in range(5):
                student = User.objects.create(
                    email=f'student{i}@test.com',
                    password='testpass123',
                    role='Student',
                    first_name=f'Student{i}',
                    last_name=f'Last{i}',
                    semester=random.randint(1, 8),
                    is_email_verified=True,
                    is_active=True
                )
                student.institution.add(institution)
                student.set_password('testpass123')
                student.save()
                students.append(student)
                logger.info(f"Created student: {student.email}")

            return institution, teachers, students
        except Exception as e:
            logger.error(f"Error creating users: {str(e)}")
            raise

    def create_courses(self, institution, teachers):
        """Create test courses with instructors and prerequisites."""
        try:
            courses = []
            course_names = ['Introduction to Programming',
                            'Data Structures', 'Database Systems', 'Web Development']

            for i, name in enumerate(course_names):
                course = Course.objects.create(
                    name=name,
                    description=f'Description for {name}',
                    institution=institution,
                    semester=random.randint(1, 8),
                    credit_hours=random.randint(2, 4),
                    total_grade=100,
                    is_active=True
                )
                # Add random teachers to course
                course.instructors.add(
                    *random.sample(teachers, random.randint(1, 2)))
                courses.append(course)
                logger.info(f"Created course: {course.name}")

            # Add prerequisites
            for i in range(1, len(courses)):
                courses[i].prerequisite_course = courses[i-1]
                courses[i].save()
                logger.info(
                    f"Added prerequisite: {courses[i-1].name} -> {courses[i].name}")

            return courses
        except Exception as e:
            logger.error(f"Error creating courses: {str(e)}")
            raise

    def create_enrollments(self, courses, students):
        """Create enrollments for students in courses."""
        try:
            enrollments = []
            for student in students:
                # Enroll student in random courses
                for course in random.sample(courses, random.randint(1, len(courses))):
                    enrollment = Enrollments.objects.create(
                        user=student,
                        course=course,
                        is_completed=random.choice([True, False])
                    )
                    enrollments.append(enrollment)
                    logger.info(
                        f"Created enrollment: {student.email} -> {course.name}")

            return enrollments
        except Exception as e:
            logger.error(f"Error creating enrollments: {str(e)}")
            raise

    def create_chapters(self, courses):
        """Create chapters for each course."""
        try:
            chapters = []
            for course in courses:
                for i in range(3):  # 3 chapters per course
                    chapter = Chapter.objects.create(
                        title=f'Chapter {i+1} - {course.name}',
                        course=course
                    )
                    chapters.append(chapter)
                    logger.info(f"Created chapter: {chapter.title}")

            return chapters
        except Exception as e:
            logger.error(f"Error creating chapters: {str(e)}")
            raise

    def create_lectures(self, chapters):
        """Create lectures for each chapter."""
        try:
            lectures = []
            for chapter in chapters:
                for i in range(2):  # 2 lectures per chapter
                    lecture = Lecture.objects.create(
                        title=f'Lecture {i+1} - {chapter.title}',
                        description=f'Description for lecture {i+1} in {chapter.title}',
                        chapter=chapter
                    )
                    lectures.append(lecture)
                    logger.info(f"Created lecture: {lecture.title}")

            return lectures
        except Exception as e:
            logger.error(f"Error creating lectures: {str(e)}")
            raise

    def create_lecture_progress(self, lectures, enrollments):
        """Create lecture progress records for students."""
        try:
            for enrollment in enrollments:
                for lecture in lectures:
                    if random.random() < 0.7:  # 70% chance of completion
                        LectureProgress.objects.create(
                            enrollment=enrollment,
                            lecture=lecture,
                            completed=True
                        )
                        logger.info(
                            f"Created lecture progress: {enrollment.user.email} -> {lecture.title}")
        except Exception as e:
            logger.error(f"Error creating lecture progress: {str(e)}")
            raise

    def create_assessments(self, courses):
        """Create assessments for each course."""
        try:
            assessments = []
            assessment_types = ['Exam', 'Assignment', 'Quiz']

            for course in courses:
                # Calculate grades to ensure they don't exceed course total grade
                remaining_grade = course.total_grade
                num_assessments = 2  # Number of assessments per course

                for i in range(num_assessments):
                    # For the last assessment, use remaining grade
                    if i == num_assessments - 1:
                        grade = remaining_grade
                    else:
                        # Distribute grades evenly among assessments
                        grade = remaining_grade // (num_assessments - i)
                        remaining_grade -= grade

                    assessment = Assessment.objects.create(
                        course=course,
                        title=f'{assessment_types[i]} {i+1} - {course.name}',
                        type=assessment_types[i],
                        due_date=timezone.now() + timedelta(days=30),
                        grade=grade,
                        start_date=timezone.now() - timedelta(days=1)
                    )
                    assessments.append(assessment)
                    logger.info(
                        f"Created assessment: {assessment.title} with grade: {grade}")

            return assessments
        except Exception as e:
            logger.error(f"Error creating assessments: {str(e)}")
            raise

    def create_mcq_questions(self, assessments, teachers):
        """Create MCQ questions for each assessment."""
        try:
            questions = []
            for assessment in assessments:
                for i in range(5):  # 5 questions per assessment
                    options = [f'Option {j}' for j in range(4)]
                    question = McqQuestion.objects.create(
                        assessment=assessment,
                        question=f'Question {i+1} for {assessment.title}',
                        options=options,
                        answer_key=options[0],  # First option is correct
                        created_by=random.choice(teachers),
                        section_number=random.randint(1, 5),
                        question_grade=Decimal('2.00')
                    )
                    questions.append(question)
                    logger.info(f"Created MCQ question: {question.question}")

            return questions
        except Exception as e:
            logger.error(f"Error creating MCQ questions: {str(e)}")
            raise

    def create_handwritten_questions(self, assessments, teachers):
        """Create handwritten questions for each assessment."""
        try:
            questions = []
            for assessment in assessments:
                for i in range(3):  # 3 handwritten questions per assessment
                    question = HandwrittenQuestion.objects.create(
                        assessment=assessment,
                        question_text=f'Handwritten Question {i+1} for {assessment.title}',
                        answer_key=f'Key points for handwritten question {i+1}',
                        max_grade=random.randint(1, 5),
                        created_by=random.choice(teachers),
                        section_number=random.randint(1, 5)
                    )
                    questions.append(question)
                    logger.info(
                        f"Created handwritten question: {question.question_text}")

            return questions
        except Exception as e:
            logger.error(f"Error creating handwritten questions: {str(e)}")
            raise

    def create_mcq_scores(self, questions, enrollments):
        """Create MCQ scores for students."""
        try:
            for enrollment in enrollments:
                # Only create scores for questions in the student's enrolled courses
                course_questions = [
                    q for q in questions if q.assessment.course == enrollment.course]
                for question in course_questions:
                    if random.random() < 0.8:  # 80% chance of answering
                        MCQQuestionScore.objects.create(
                            question=question,
                            enrollment=enrollment,
                            selected_answer=random.choice(question.options),
                            score=Decimal(
                                str(random.uniform(0, float(question.question_grade))))
                        )
                        logger.info(
                            f"Created MCQ score for {enrollment.user.email} -> {question.question}")
        except Exception as e:
            logger.error(f"Error creating MCQ scores: {str(e)}")
            raise

    def create_handwritten_scores(self, questions, enrollments):
        """Create handwritten question scores for students."""
        try:
            for enrollment in enrollments:
                # Only create scores for questions in the student's enrolled courses
                course_questions = [
                    q for q in questions if q.assessment.course == enrollment.course]
                for question in course_questions:
                    if random.random() < 0.7:  # 70% chance of answering
                        score = random.uniform(0, question.max_grade)
                        HandwrittenQuestionScore.objects.create(
                            question=question,
                            enrollment=enrollment,
                            score=Decimal(str(score)),
                            feedback=f'Feedback for student {enrollment.user.email}',
                            extracted_text=f'Extracted text from student answer {enrollment.user.email}'
                        )
                        logger.info(
                            f"Created handwritten score for {enrollment.user.email} -> {question.question_text}")
        except Exception as e:
            logger.error(f"Error creating handwritten scores: {str(e)}")
            raise

    def create_assessment_scores(self, assessments, enrollments):
        """Create assessment scores for students."""
        try:
            for enrollment in enrollments:
                for assessment in assessments:
                    if assessment.course == enrollment.course:
                        # Calculate total score
                        mcq_total = assessment.mcq_questions.filter(
                            scores__enrollment=enrollment
                        ).aggregate(total=models.Sum('scores__score'))['total'] or 0

                        handwritten_total = assessment.handwritten_questions.filter(
                            scores__enrollment=enrollment
                        ).aggregate(total=models.Sum('scores__score'))['total'] or 0

                        total_score = mcq_total + handwritten_total

                        # Use get_or_create to avoid duplicates
                        AssessmentScore.objects.get_or_create(
                            enrollment=enrollment,
                            assessment=assessment,
                            defaults={'total_score': total_score}
                        )
                        logger.info(
                            f"Created assessment score for {enrollment.user.email} -> {assessment.title}")
        except Exception as e:
            logger.error(f"Error creating assessment scores: {str(e)}")
            raise
