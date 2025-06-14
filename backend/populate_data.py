import os
import django
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal
from django.db import models

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from users.models import User
from courses.models import Course
from chapter.models import Chapter
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore
from mcqQuestion.models import McqQuestion
from MCQQuestionScore.models import MCQQuestionScore
from HandwrittenQuestion.models import HandwrittenQuestion, HandwrittenQuestionScore
from enrollments.models import Enrollments

def create_users():
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
        student.institution.set([institution])
        student.set_password('testpass123')
        student.save()
        students.append(student)

    return institution, teachers, students

def create_courses(institution, teachers):
    courses = []
    course_names = ['Introduction to Programming', 'Data Structures', 'Database Systems', 'Web Development']
    
    for i, name in enumerate(course_names):
        course = Course.objects.create(
            name=name,
            description=f'Description for {name}',
            institution=institution,
            semester=random.randint(1, 8),
            credit_hours=random.randint(2, 4)
        )
        # Add random teachers to course
        course.instructors.add(*random.sample(teachers, random.randint(1, 2)))
        courses.append(course)

    # Add prerequisites
    for i in range(1, len(courses)):
        courses[i].prerequisite_course = courses[i-1]
        courses[i].save()

    return courses

def create_enrollments(courses, students):
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
    return enrollments

def create_chapters(courses):
    chapters = []
    for course in courses:
        for i in range(3):  # 3 chapters per course
            chapter = Chapter.objects.create(
                title=f'Chapter {i+1} - {course.name}',
                course=course
            )
            chapters.append(chapter)
    return chapters

def create_lectures(chapters):
    lectures = []
    for chapter in chapters:
        for i in range(2):  # 2 lectures per chapter
            lecture = Lecture.objects.create(
                title=f'Lecture {i+1} - {chapter.title}',
                description=f'Description for lecture {i+1} in {chapter.title}',
                chapter=chapter
            )
            lectures.append(lecture)
    return lectures

def create_lecture_progress(lectures, students):
    for student in students:
        for lecture in lectures:
            if random.random() < 0.7:  # 70% chance of completion
                LectureProgress.objects.create(
                    user=student,
                    lecture=lecture,
                    completed=True
                )

def create_assessments(courses):
    assessments = []
    assessment_types = ['Exam', 'Assignment', 'Quiz']
    
    for course in courses:
        for i in range(2):  # 2 assessments per course
            assessment = Assessment.objects.create(
                course=course,
                title=f'{assessment_types[i]} {i+1} - {course.name}',
                type=assessment_types[i],
                due_date=timezone.now() + timedelta(days=30),
                grade=random.randint(40, 70),
                start_date=timezone.now() - timedelta(days=1)
            )
            assessments.append(assessment)
    return assessments

def create_mcq_questions(assessments, teachers):
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
    return questions

def create_handwritten_questions(assessments, teachers):
    questions = []
    for assessment in assessments:
        for i in range(3):  # 3 handwritten questions per assessment
            question = HandwrittenQuestion.objects.create(
                assessment=assessment,
                question_text=f'Handwritten Question {i+1} for {assessment.title}',
                answer_key=f'Key points for handwritten question {i+1}',
                max_grade=random.randint(1, 5),
                created_by=random.choice(teachers)
            )
            questions.append(question)
    return questions

def create_mcq_scores(questions, enrollments):
    for enrollment in enrollments:
        # Only create scores for questions in the student's enrolled courses
        course_questions = [q for q in questions if q.assessment.course == enrollment.course]
        for question in course_questions:
            if random.random() < 0.8:  # 80% chance of answering
                MCQQuestionScore.objects.create(
                    question=question,
                    enrollment=enrollment,
                    selected_answer=random.choice(question.options)
                )

def create_handwritten_scores(questions, enrollments):
    for enrollment in enrollments:
        # Only create scores for questions in the student's enrolled courses
        course_questions = [q for q in questions if q.assessment.course == enrollment.course]
        for question in course_questions:
            if random.random() < 0.7:  # 70% chance of answering
                score = random.uniform(0, question.max_grade)
                HandwrittenQuestionScore.objects.create(
                    question=question,
                    enrollment=enrollment,
                    score=score,
                    feedback=f'Feedback for student {enrollment.user.email}',
                    extracted_text=f'Extracted text from student answer {enrollment.user.email}'
                )

def create_assessment_scores(assessments, enrollments):
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

def main():
    print("Creating users...")
    institution, teachers, students = create_users()
    
    print("Creating courses...")
    courses = create_courses(institution, teachers)
    
    print("Creating enrollments...")
    enrollments = create_enrollments(courses, students)
    
    print("Creating chapters...")
    chapters = create_chapters(courses)
    
    print("Creating lectures...")
    lectures = create_lectures(chapters)
    
    print("Creating lecture progress...")
    create_lecture_progress(lectures, students)
    
    print("Creating assessments...")
    assessments = create_assessments(courses)
    
    print("Creating MCQ questions...")
    mcq_questions = create_mcq_questions(assessments, teachers)
    
    print("Creating Handwritten questions...")
    handwritten_questions = create_handwritten_questions(assessments, teachers)
    
    print("Creating MCQ scores...")
    create_mcq_scores(mcq_questions, enrollments)
    
    print("Creating Handwritten scores...")
    create_handwritten_scores(handwritten_questions, enrollments)
    
    print("Creating Assessment scores...")
    create_assessment_scores(assessments, enrollments)
    
    print("Data population completed!")

if __name__ == '__main__':
    main() 