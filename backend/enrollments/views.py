from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from users.permissions import isInstitution, isStudent, isTeacher
from decimal import Decimal
from collections import defaultdict


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
            user=user,
            is_completed=False
        ).values_list('course_id', flat=True)

        return Course.objects.filter(id__in=enrolled_course_ids)


class PromoteStudentsAPIView(APIView):
    permission_classes = [isInstitution]

    def post(self, request):
        user = request.user

        policy = InstitutionPolicy.objects.filter(institution=user).first()

        students = User.objects.filter(role="Student", institution=user)

        for student in students:
            enrollments = Enrollments.objects.filter(
                course__institution=user,
                user=student,
                is_completed=False,
                is_summer_enrollment=False
            )
            failed_courses_count = 0
            total_semester_score = 0
            total_semester_grade = 0
            has_summer = False
            failed_courses = []

            for enrollment in enrollments:
                total_semester_score += enrollment.total_score
                total_semester_grade += enrollment.course.total_grade or 0
                print(enrollment.course.name)
                print(str(enrollment.total_score) + " / " +
                      str(enrollment.course.passing_grade))
                if enrollment.total_score >= enrollment.course.passing_grade:
                    enrollment.is_passed = True
                    enrollment.save()
                else:
                    if getattr(user, 'institution_type', None) == "school":
                        failed_courses.append(enrollment.course.id)
                    has_summer = True
                    failed_courses_count += 1
                    enrollment.save()
                enrollment.is_completed = True
                enrollment.save()
            if total_semester_grade > 0:
                percentage = (total_semester_score /
                              total_semester_grade) * 100
            else:
                percentage = 0

            print(
                f"Total: {total_semester_score} / {total_semester_grade} -> {percentage:.2f}%")

            should_retain = False

            if policy and policy.max_allowed_failures:
                if failed_courses_count > policy.max_allowed_failures:
                    should_retain = True

            if policy and policy.min_passing_percentage:
                if percentage < policy.min_passing_percentage:
                    should_retain = True

            if should_retain:

                level_start_semester = ((student.semester - 1) // 2) * 2 + 1

                if getattr(user, 'institution_type', None) == "school":
                    student.semester = level_start_semester
                    student.save()
                    matching_courses = Course.objects.filter(
                        semester=student.semester,
                        institution=user
                    )
                    for course in matching_courses:
                        Enrollments.objects.create(user=student, course=course)
                else:
                    student.semester = level_start_semester
                    student.save()
                    level_semesters = [level_start_semester,
                                       level_start_semester + 1]

                    failed_enrollments = Enrollments.objects.filter(
                        user=student,
                        course__semester__in=level_semesters,
                        course__institution=user
                    )
                    for enrollment in failed_enrollments:
                        enrollment.is_passed = False
                        enrollment.is_completed = True
                        enrollment.save()

            elif not has_summer and getattr(user, 'institution_type', None) == "school":
                student.semester += 1
                student.save()
                matching_courses = Course.objects.filter(
                    semester=student.semester,
                    institution=user
                )
                for course in matching_courses:
                    Enrollments.objects.create(user=student, course=course)
                    lectures = Lecture.objects.filter(chapter__course=course)
                    LectureProgress.objects.bulk_create([
                        LectureProgress(user=student, lecture=lecture)
                        for lecture in lectures
                    ])
            elif getattr(user, 'institution_type', None) == "school" and has_summer:
                matching_courses = Course.objects.filter(
                    id__in=failed_courses
                )
                for course in matching_courses:
                    Enrollments.objects.create(
                        user=student, course=course, is_summer_enrollment=True)
            elif getattr(user, 'institution_type', None) == "faculty":
                student.semester += 1
                student.save()

        return Response({
            "message": "Promotion process completed successfully.",
        }, status=200)


class PromoteStudentsSummerAPIView(APIView):
    permission_classes = [isInstitution]

    def post(self, request):
        user = request.user

        students = User.objects.filter(role="Student", institution=user)

        for student in students:
            enrollments = Enrollments.objects.filter(
                course__institution=user,
                user=student,
                is_completed=False,
                is_summer_enrollment=True
            )

            failed_courses_count = 0

            for enrollment in enrollments:
                if enrollment.total_score >= enrollment.course.passing_grade:
                    enrollment.is_passed = True
                    enrollment.save()
                else:
                    failed_courses_count += 1
                enrollment.is_completed = True
                enrollment.save()

            level_start_semester = ((student.semester - 1) // 2) * 2 + 1

            if failed_courses_count and getattr(user, 'institution_type', None) == "school":
                student.semester = level_start_semester
                student.save()
                matching_courses = Course.objects.filter(
                    semester=student.semester,
                    institution=user
                )
                for course in matching_courses:
                    Enrollments.objects.create(user=student, course=course)
            elif getattr(user, 'institution_type', None) == "school":
                student.semester += 1
                student.save()
                matching_courses = Course.objects.filter(
                    semester=student.semester,
                    institution=user
                )
                for course in matching_courses:
                    Enrollments.objects.create(user=student, course=course)
                    lectures = Lecture.objects.filter(chapter__course=course)
                    LectureProgress.objects.bulk_create([
                        LectureProgress(user=student, lecture=lecture)
                        for lecture in lectures
                    ])
        return Response({
            "message": "Promotion process completed successfully.",
        }, status=200)


class AllStudentGradesView(APIView):
    permission_classes = [isStudent]

    def get(self, request):
        student = request.user

        student_data = {
            "student_id": str(student.id),
            "student_name": f"{student.first_name} {student.middle_name} {student.last_name}",
            "grades": []
        }

        enrollments = (
            Enrollments.objects
            .filter(user=student)
            .select_related('course')
            .order_by('course_id', '-enrolled_at')
        )

        seen_courses = set()

        for enrollment in enrollments:
            course_id = enrollment.course.id
            if course_id in seen_courses:
                continue

            seen_courses.add(course_id)

            course_name = (
                f"{enrollment.course.name} (Summer)"
                if enrollment.is_summer_enrollment else
                enrollment.course.name
            )

            student_data["grades"].append({
                "course_id": str(course_id),
                "course_name": course_name,
                "grade": enrollment.total_score,
                "total_grade": enrollment.course.total_grade,
                "status": "in progress" if not enrollment.is_passed and enrollment.is_completed else "passed" if enrollment.is_passed and enrollment.is_completed else "failed",
                "semester": enrollment.course.semester
            })

        return Response(student_data)


class EligibleCoursesAPIView(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EnrollMultipleCoursesSerializer
        return CourseSerializer

    permission_classes = [isStudent]

    def get_queryset(self):
        user = self.request.user

        policy = InstitutionPolicy.objects.filter(
            institution=user.institution.first()).first()
        if not policy:
            raise PermissionDenied("No institution policy found.")

        if policy.year_registration_open:

            previous_courses = Course.objects.filter(is_active=True)
            current_courses = Course.objects.filter(
                is_active=True, semester=user.semester)

            eligible_courses = []

            for course in previous_courses:
                last_enrollment = Enrollments.objects.filter(
                    user=user, course=course).order_by('-enrolled_at').first()

                if last_enrollment:
                    if not last_enrollment.is_passed and last_enrollment.is_completed:
                        eligible_courses.append(course)

            for course in current_courses:
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

            all_active_courses = Course.objects.filter(
                is_active=True,
                is_summer_open=True
            ).filter(
                Q(semester=user.semester - 1) | Q(semester=user.semester - 2)
            )

            eligible_courses = []

            for course in all_active_courses:
                last_enrollment = Enrollments.objects.filter(
                    user=user, course=course).order_by('-enrolled_at').first()
                if last_enrollment:
                    if not last_enrollment.is_passed and last_enrollment.is_completed:
                        eligible_courses.append(course)
                    continue

            return eligible_courses

        raise PermissionDenied("Registration is not open yet.")

    def create(self, request, *args, **kwargs):
        user = request.user

        policy = InstitutionPolicy.objects.filter(
            institution=user.institution.first()).first()
        if not policy:
            raise PermissionDenied("No institution policy found.")

        if not (policy.year_registration_open or policy.summer_registration_open):
            raise PermissionDenied("Registration is not open yet.")

        course_ids = request.data.get("courses", [])

        if len(course_ids) > policy.max_allowed_courses_per_semester:
            return Response({"error": "You can only register up to " + str(policy.max_allowed_courses_per_semester) + " courses"}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(course_ids, list) or not course_ids:
            return Response({"error": "Please provide a list of course IDs."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course_uuids = [UUID(cid) for cid in course_ids]
        except ValueError:
            return Response({"error": "One or more course IDs are invalid UUIDs."}, status=status.HTTP_400_BAD_REQUEST)

        eligible_courses = self.get_queryset()
        eligible_course_dict = {
            course.id: course for course in eligible_courses}

        if not all(cid in eligible_course_dict for cid in course_uuids):
            return Response({"error": "One or more selected courses are not eligible for enrollment."}, status=status.HTTP_400_BAD_REQUEST)

        enrolled_courses = []

        for course_id in course_uuids:
            course = eligible_course_dict[course_id]
            if policy.summer_registration_open:
                enrollment = Enrollments.objects.create(
                    user=user, course=course, is_summer_enrollment=True)
                enrolled_courses.append(enrollment)
            elif policy.year_registration_open:
                enrollment = Enrollments.objects.create(
                    user=user, course=course)
                enrolled_courses.append(enrollment)
                lectures = Lecture.objects.filter(chapter__course=course)
                progress_entries = [LectureProgress(
                    user=user, lecture=lecture) for lecture in lectures]
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
            raise PermissionDenied(
                "You can only view your own enrollment scores")
        elif user.role == 'Teacher' and not enrollment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied(
                "You can only view scores for courses you teach")
        elif user.role == 'Institution' and enrollment.course.institution != user:
            raise PermissionDenied(
                "You can only view scores for your institution's courses")

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
            raise PermissionDenied(
                "You can only update scores for courses you teach")
        elif user.role == 'Institution' and enrollment.course.institution != user:
            raise PermissionDenied(
                "You can only update scores for your institution's courses")

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
