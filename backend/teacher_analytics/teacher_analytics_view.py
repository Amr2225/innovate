from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from courses.models import Course
from enrollments.models import Enrollments

class TeacherAnalyticsView(generics.GenericAPIView):
    """
    API endpoint for teacher analytics.
    Provides active student count for courses taught by the teacher.
    
    GET /api/teacher-analytics/
    
    Returns:
    {
        "courses": [
            {
                "course_id": "uuid",
                "course_name": "string",
                "active_students": integer
            }
        ],
        "overall_statistics": {
            "total_courses": integer,
            "total_active_students": integer
        }
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == "Teacher":
            courses = Course.objects.filter(instructors=request.user)        
            courses_data = []
            total_active_students = 0
            for course in courses:
                # Get only active students (is_completed=False)
                active_students = Enrollments.objects.filter(
                    course=course,
                    is_completed=False
                ).count()
                
                course_data = {
                    "course_id": str(course.id),
                    "course_name": course.name,
                    "active_students": active_students
                }
                
                courses_data.append(course_data)
                total_active_students += active_students
            
            response_data = {
                "courses": courses_data,
                "overall_statistics": {
                    "total_courses": courses.count(),
                    "total_active_students": total_active_students
                }
            }
            
            return Response(response_data) 

        elif request.user.role == "Institution":
            courses = Course.objects.filter(institution=request.user)        
            courses_data = []
            total_active_students = 0
            for course in courses:
                # Get only active students (is_completed=False)
                active_students = Enrollments.objects.filter(
                    course=course,
                    is_completed=False
                ).count()
                
                course_data = {
                    "course_id": str(course.id),
                    "course_name": course.name,
                    "active_students": active_students
                }
                
                courses_data.append(course_data)
                total_active_students += active_students
            
            response_data = {
                "courses": courses_data,
                "overall_statistics": {
                    "total_courses": courses.count(),
                    "total_active_students": total_active_students
                }
            }
            
            return Response(response_data) 
