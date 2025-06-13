from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore

class StudentAnalyticsView(generics.GenericAPIView):
    """
    API endpoint for student analytics.
    
    GET /api/teacher-analytics/students/ - Returns analytics for all courses
    GET /api/teacher-analytics/students/{course_id}/ - Returns analytics for a specific course
    
    Returns:
    {
        "courses": [
            {
                "course_id": "uuid",
                "course_name": "string",
                "students": [
                    {
                        "student_id": "uuid",
                        "student_name": "string",
                        "progress": {
                            "completed_lectures": integer,
                            "total_lectures": integer,
                            "completion_percentage": float
                        },
                        "assessments": [
                            {
                                "assessment_id": "uuid",
                                "assessment_name": "string",
                                "score": float,
                                "submitted_at": "datetime"
                            }
                        ],
                        "average_score": float
                    }
                ],
                "course_statistics": {
                    "total_students": integer,
                    "average_completion": float,
                    "average_score": float
                }
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id=None):
        if request.user.role != "Teacher":
            return Response(
                {"detail": "Only teachers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get courses taught by the teacher
        if course_id:
            try:
                courses = [Course.objects.get(id=course_id, instructors=request.user)]
            except Course.DoesNotExist:
                return Response(
                    {"detail": "Course not found or you don't have permission to access it"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            courses = Course.objects.filter(instructors=request.user)

        courses_data = []
        
        for course in courses:
            # Get all enrollments for the course
            enrollments = Enrollments.objects.filter(course=course)
            total_lectures = Lecture.objects.filter(chapter__course=course).count()
            
            students_data = []
            total_completion = 0
            total_score = 0
            student_count = 0
            
            for enrollment in enrollments:
                # Get student's lecture progress
                completed_lectures = LectureProgress.objects.filter(
                    enrollment=enrollment,
                    completed=True
                ).count()
                
                completion_percentage = (completed_lectures / total_lectures * 100) if total_lectures > 0 else 0
                
                # Get student's assessment scores
                assessment_scores = AssessmentScore.objects.filter(
                    enrollment=enrollment,
                    assessment__course=course
                ).select_related('assessment')
                
                assessments_data = []
                total_student_score = 0
                assessment_count = 0
                
                for score in assessment_scores:
                    assessment_data = {
                        "assessment_id": str(score.assessment.id),
                        "assessment_name": score.assessment.title,
                        "score": float(score.total_score),
                        "submitted_at": score.created_at
                    }
                    assessments_data.append(assessment_data)
                    total_student_score += float(score.total_score)
                    assessment_count += 1
                
                average_score = (total_student_score / assessment_count) if assessment_count > 0 else 0
                
                student_data = {
                    "student_id": str(enrollment.user.id),
                    "student_name": f"{enrollment.user.first_name} {enrollment.user.last_name}",
                    "progress": {
                        "completed_lectures": completed_lectures,
                        "total_lectures": total_lectures,
                        "completion_percentage": round(completion_percentage, 2)
                    },
                    "assessments": assessments_data,
                    "average_score": round(average_score, 2)
                }
                
                students_data.append(student_data)
                total_completion += completion_percentage
                total_score += average_score
                student_count += 1
            
            # Calculate course statistics
            course_statistics = {
                "total_students": student_count,
                "average_completion": round(total_completion / student_count, 2) if student_count > 0 else 0,
                "average_score": round(total_score / student_count, 2) if student_count > 0 else 0
            }
            
            course_data = {
                "course_id": str(course.id),
                "course_name": course.name,
                "students": students_data,
                "course_statistics": course_statistics
            }
            
            courses_data.append(course_data)
        
        response_data = {
            "courses": courses_data
        }
        
        return Response(response_data) 