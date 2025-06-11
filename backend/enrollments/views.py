from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from users.permissions import isInstitution, isStudent, isTeacher
from decimal import Decimal

from courses.models import Course
from enrollments.models import Enrollments
from rest_framework.views import APIView
from courses.serializers import CourseSerializer
import uuid
from uuid import UUID
from assessment.models import AssessmentScore
from institution_policy.models import InstitutionPolicy
from users.models import User
from enrollments.serializers import (
    EnrollMultipleCoursesSerializer,
    EnrollmentsSerializer,
    AssessmentScoreSerializer
)
from lecture.models import Lecture, LectureProgress

class EnrolledCoursesAPIView(generics.ListAPIView):
    permission_classes = [isStudent]
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        enrolled_course_ids = Enrollments.objects.filter(
            user=user
        ).values_list('course_id', flat=True)

        return Course.objects.filter(id__in=enrolled_course_ids)



class PromoteStudentsFacultyAPIView(APIView):
    permission_classes = [isInstitution]

    def post(self, request):
        user = request.user

        semester = request.data.get("semester")
        if semester is None:
            return Response({"detail": "Semester is required."}, status=400)

        policy = InstitutionPolicy.objects.filter(institution=user).first()

        students = User.objects.filter(role="Student", semester=semester, institution=user)

        promoted_students = []
        retained_students = []

        for student in students:
            enrollments = Enrollments.objects.filter(
                course__institution=user,
                user=student,
                is_completed=False
            )

            failed_courses_count = 0
            total_semester_score = 0
            total_semester_grade = 0
            print(student)

            for enrollment in enrollments:
                total_semester_score += enrollment.total_score
                total_semester_grade += enrollment.course.total_grade or 0
                print(enrollment.course.name)
                print(str(enrollment.total_score) + " / " + str(enrollment.course.passing_grade))
                if enrollment.total_score >= enrollment.course.passing_grade:
                    enrollment.is_passed = True
                    enrollment.save()
                else:
                    failed_courses_count += 1
                    enrollment.save()
                enrollment.is_completed = True
                enrollment.save()
            if total_semester_grade > 0:
                percentage = (total_semester_score / total_semester_grade) * 100
            else:
                percentage = 0

            print(f"Total: {total_semester_score} / {total_semester_grade} -> {percentage:.2f}%")

            should_retain = False
            
            if policy and policy.max_allowed_failures:
                if failed_courses_count > policy.max_allowed_failures:
                    should_retain = True
            
            if policy and policy.min_passing_percentage:
                if percentage < policy.min_passing_percentage:
                    should_retain = True
            
            if should_retain:
                retained_students.append(student.id)
            else:
                student.semester += 1
                student.save()
                promoted_students.append(student.id)
        
        return Response({
            "promoted_students": promoted_students,
            "retained_students": retained_students
        }, status=200)



class EligibleCoursesAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EnrollMultipleCoursesSerializer
        return CourseSerializer
    
    permission_classes = [isStudent]

    def get_queryset(self):
        user = self.request.user

        policy = InstitutionPolicy.objects.filter(institution=user.institution.first()).first()
        if not policy:
            raise PermissionDenied("No institution policy found.")
        
        if policy.year_registration_open:
            all_active_courses = Course.objects.filter(is_active=True)

            eligible_courses = []

            for course in all_active_courses:
                last_enrollment = Enrollments.objects.filter(user=user, course=course).order_by('-enrolled_at').first()

                if last_enrollment:
                    if not last_enrollment.is_passed and last_enrollment.is_completed:
                        eligible_courses.append(course)
                    continue
                else:
                    prereq = course.prerequisite_course
                    completed_course_ids = Enrollments.objects.filter(
                        user=user,
                        is_passed=True,
                        is_completed=True
                    ).values_list('course_id', flat=True)

                    if (not prereq or prereq.id in completed_course_ids) and course.semester <= user.semester:
                        eligible_courses.append(course)

            return eligible_courses
        
        elif policy.summer_registration_open:

            all_active_courses = Course.objects.filter(is_active=True, is_summer_open=True)
            
            eligible_courses = []
            
            for course in all_active_courses:
                last_enrollment = Enrollments.objects.filter(user=user, course=course).order_by('-enrolled_at').first()
                if last_enrollment:
                    if not last_enrollment.is_passed and last_enrollment.is_completed:
                        eligible_courses.append(course)
                    continue
            
            return eligible_courses
        
        raise PermissionDenied("Registration is not open yet.")
    
    def create(self, request, *args, **kwargs):
        user = request.user

        policy = InstitutionPolicy.objects.filter(institution=user.institution.first()).first()
        if not policy:
            raise PermissionDenied("No institution policy found.")

        if not (policy.year_registration_open or policy.summer_registration_open):
            raise PermissionDenied("Registration is not open yet.")
        
        course_ids = request.data.get("courses", [])

        if not isinstance(course_ids, list) or not course_ids:
            return Response({"error": "Please provide a list of course IDs."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course_uuids = [UUID(cid) for cid in course_ids]
        except ValueError:
            return Response({"error": "One or more course IDs are invalid UUIDs."}, status=status.HTTP_400_BAD_REQUEST)

        eligible_courses = self.get_queryset()
        eligible_course_dict = {course.id: course for course in eligible_courses}
        
        if not all(cid in eligible_course_dict for cid in course_uuids):
            return Response({"error": "One or more selected courses are not eligible for enrollment."}, status=status.HTTP_400_BAD_REQUEST)
        
        enrolled_courses = []

        for course_id in course_uuids:
            course = eligible_course_dict[course_id]
            if policy.summer_registration_open:
                enrollment = Enrollments.objects.create(user=user, course=course, is_summer_enrollment=True)
                enrolled_courses.append(enrollment)
            elif policy.year_registration_open:
                enrollment = Enrollments.objects.create(user=user, course=course)
                enrolled_courses.append(enrollment)
                lectures = Lecture.objects.filter(chapter__course=course)
                progress_entries = [LectureProgress(user=user, lecture=lecture) for lecture in lectures]
                try:
                    LectureProgress.objects.bulk_create(progress_entries)
                except Exception as e:
                    print(f"Error creating progress entries: {e}")

        return Response({
        "enrolled": EnrollmentsSerializer(enrolled_courses, many=True, context={'request': request}).data
    }, status=status.HTTP_201_CREATED)


class EnrollmentAssessmentScoresView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentScoreSerializer

    def get_queryset(self):
        enrollment_id = self.kwargs.get('enrollment_id')
        enrollment = get_object_or_404(Enrollments, id=enrollment_id)
        
        # Check permissions
        user = self.request.user
        if user.role == 'Student' and enrollment.user != user:
            return AssessmentScore.objects.none()
        elif user.role == 'Teacher' and not enrollment.course.instructors.filter(id=user.id).exists():
            return AssessmentScore.objects.none()
        elif user.role == 'Institution' and enrollment.course.institution != user:
            return AssessmentScore.objects.none()
            
        return AssessmentScore.objects.filter(enrollment=enrollment).select_related('assessment').order_by('-submitted_at')

class EnrollmentScoreView(generics.RetrieveAPIView):
    """
    API view to get the total score for a specific enrollment
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EnrollmentsSerializer

    def get_object(self):
        enrollment_id = self.kwargs.get('enrollment_id')
        enrollment = get_object_or_404(Enrollments, id=enrollment_id)
        
        # Check permissions
        user = self.request.user
        if user.role == 'Student' and enrollment.user != user:
            raise PermissionDenied("You can only view your own enrollment scores")
        elif user.role == 'Teacher' and not enrollment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You can only view scores for courses you teach")
        elif user.role == 'Institution' and enrollment.course.institution != user:
            raise PermissionDenied("You can only view scores for your institution's courses")
            
        return enrollment

class EnrollmentUpdateScoreView(generics.UpdateAPIView):
    """
    API view to update the total score for a specific enrollment
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EnrollmentsSerializer
    queryset = Enrollments.objects.all()

    def update(self, request, *args, **kwargs):
        enrollment = self.get_object()
        user = request.user

        # Check permissions
        if user.role == 'Student':
            raise PermissionDenied("Students cannot update scores")
        elif user.role == 'Teacher' and not enrollment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You can only update scores for courses you teach")
        elif user.role == 'Institution' and enrollment.course.institution != user:
            raise PermissionDenied("You can only update scores for your institution's courses")

        # Get the new score from request data
        new_score = request.data.get('total_score')
        if new_score is None:
            return Response({"error": "total_score is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convert to Decimal and validate
            score = Decimal(str(new_score))
            if score < 0 or score > 100:
                return Response(
                    {"error": "Score must be between 0 and 100"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the score
            enrollment.total_score = score
            enrollment.save()
            
            return Response(
                self.get_serializer(enrollment).data,
                status=status.HTTP_200_OK
            )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid score value"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
