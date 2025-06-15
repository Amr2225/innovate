from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from courses.models import Course
from enrollments.models import Enrollments


class TopStudentsView(generics.GenericAPIView):
    """
    API endpoint for top students in a course.

    GET /api/teacher-analytics/top-students/{course_id}/ - Returns top 5 students by total grade

    Returns:
    {
        "course_id": "uuid",
        "course_name": "string",
        "top_students": [
            {
                "student_id": "uuid",
                "student_name": "string",
                "total_grade": float
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        user = request.user
        if user.role == "Teacher":
            course_filter = {'id': course_id, 'instructors': user}
        elif user.role == "Institution":
            course_filter = {'id': course_id, 'institution': user}
        else:
            return Response(
                {"detail": "Only teachers and institutions can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            course = Course.objects.get(**course_filter)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found or you don't have permission to access it"},
                status=status.HTTP_404_NOT_FOUND
            )

        top_enrollments = Enrollments.objects.filter(
            course=course
        ).order_by('-total_score')[:5]

        top_students = []
        for enrollment in top_enrollments:
            student_data = {
                "student_id": str(enrollment.user.id),
                "student_name": f"{enrollment.user.first_name} {enrollment.user.last_name}",
                "total_grade": float(enrollment.total_score)
            }
            top_students.append(student_data)

        response_data = {
            "course_id": str(course.id),
            "course_name": course.name,
            "top_students": top_students
        }

        return Response(response_data)
