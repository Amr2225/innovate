from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from courses.models import Course
from chapter.models import Chapter
from lecture.models import Lecture, LectureProgress
from enrollments.models import Enrollments
from assessment.models import Assessment, AssessmentScore
from mcqQuestion.models import McqQuestion
import uuid
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create Institution
        institution = User.objects.create(
            email='institution@example.com',
            password='institution123',
            role='Institution',
            institution_type='FACULTY',
            name='Sample University',
            credits=100,
            is_email_verified=True,
            is_active=True
        )
        institution.set_password('institution123')
        institution.save()

        # Create Teachers
        teacher1 = User.objects.create(
            email='teacher1@example.com',
            password='teacher123',
            role='Teacher',
            first_name='John',
            last_name='Doe',
            is_email_verified=True,
            is_active=True
        )
        teacher1.set_password('teacher123')
        teacher1.save()

        teacher2 = User.objects.create(
            email='teacher2@example.com',
            password='teacher123',
            role='Teacher',
            first_name='Jane',
            last_name='Smith',
            is_email_verified=True,
            is_active=True
        )
        teacher2.set_password('teacher123')
        teacher2.save()

        # Create Students
        student1 = User.objects.create(
            email='student1@example.com',
            password='student123',
            role='Student',
            first_name='Alice',
            last_name='Johnson',
            semester=1,
            is_email_verified=True,
            is_active=True
        )
        student1.set_password('student123')
        student1.save()

        student2 = User.objects.create(
            email='student2@example.com',
            password='student123',
            role='Student',
            first_name='Bob',
            last_name='Wilson',
            semester=2,
            is_email_verified=True,
            is_active=True
        )
        student2.set_password('student123')
        student2.save()

        # Create Courses
        course1 = Course.objects.create(
            name='Introduction to Programming',
            description='Learn the basics of programming',
            institution=institution,
            semester=1,
            credit_hours=3
        )
        course1.instructors.add(teacher1)

        course2 = Course.objects.create(
            name='Advanced Programming',
            description='Advanced programming concepts',
            institution=institution,
            semester=2,
            credit_hours=3,
            prerequisite_course=course1
        )
        course2.instructors.add(teacher2)

        # Create Chapters
        chapter1 = Chapter.objects.create(
            title='Introduction to Python',
            course=course1
        )

        chapter2 = Chapter.objects.create(
            title='Variables and Data Types',
            course=course1
        )

        chapter3 = Chapter.objects.create(
            title='Object-Oriented Programming',
            course=course2
        )

        # Create Lectures
        lecture1 = Lecture.objects.create(
            title='What is Python?',
            description='Introduction to Python programming language',
            chapter=chapter1
        )

        lecture2 = Lecture.objects.create(
            title='Variables in Python',
            description='Understanding variables and their types',
            chapter=chapter2
        )

        lecture3 = Lecture.objects.create(
            title='Classes and Objects',
            description='Introduction to OOP concepts',
            chapter=chapter3
        )

        # Create Lecture Progress
        LectureProgress.objects.create(
            user=student1,
            lecture=lecture1,
            completed=True
        )

        LectureProgress.objects.create(
            user=student1,
            lecture=lecture2,
            completed=False
        )

        # Create Enrollments
        Enrollments.objects.create(
            user=student1,
            course=course1,
            is_completed=False
        )

        Enrollments.objects.create(
            user=student2,
            course=course2,
            is_completed=False
        )

        # Create Assessments
        assessment1 = Assessment.objects.create(
            course=course1,
            institution=teacher1,
            title='Python Basics Quiz',
            type='Quiz',
            due_date=timezone.now() + timedelta(days=7),
            grade=10
        )

        assessment2 = Assessment.objects.create(
            course=course2,
            institution=teacher2,
            title='OOP Final Exam',
            type='Exam',
            due_date=timezone.now() + timedelta(days=14),
            grade=50
        )

        # Create Assessment Scores
        AssessmentScore.objects.create(
            assessment=assessment1,
            student=student1,
            score=8,
            submit_date=timezone.now()
        )

        # Create MCQ Questions
        McqQuestion.objects.create(
            assessment=assessment1,
            question='What is Python?',
            answer={
                'A': 'A snake',
                'B': 'A programming language',
                'C': 'A game',
                'D': 'A database'
            },
            answer_key='B',
            created_by=teacher1
        )

        self.stdout.write(self.style.SUCCESS(
            'Successfully populated database with sample data'))
