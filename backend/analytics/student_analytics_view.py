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
    
    GET /api/analytics/students/ - Returns analytics for all courses
    GET /api/analytics/students/{course_id}/ - Returns analytics for a specific course
    
    Accessible by: Teachers (only their courses) & Institutions (only their courses)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id=None):
        user = request.user

        # Only Teachers or Institutions can access
        if user.role not in ["Teacher", "Institution"]:
            return Response(
                {"detail": "Only teachers or institutions can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve courses based on role and course_id
        try:
            if course_id:
                if user.role == "Teacher":
                    courses = [Course.objects.get(id=course_id, instructors=user)]
                else:  # Institution
                    courses = [Course.objects.get(id=course_id, institution=user)]
            else:
                if user.role == "Teacher":
                    courses = Course.objects.filter(instructors=user)
                else:  # Institution
                    courses = Course.objects.filter(institution=user)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found or you don't have permission to access it"},
                status=status.HTTP_404_NOT_FOUND
            )

        courses_data = []
        
        for course in courses:
            enrollments = Enrollments.objects.filter(course=course)
            total_lectures = Lecture.objects.filter(chapter__course=course).count()
            
            students_data = []
            total_completion = 0
            total_score = 0
            student_count = 0
            
            for enrollment in enrollments:
                completed_lectures = LectureProgress.objects.filter(
                    enrollment=enrollment,
                    completed=True
                ).count()
                
                completion_percentage = (completed_lectures / total_lectures * 100) if total_lectures else 0
                
                assessment_scores = AssessmentScore.objects.filter(
                    enrollment=enrollment,
                    assessment__course=course
                ).select_related('assessment')
                
                assessments_data = []
                total_student_score = 0
                assessment_count = 0
                
                for score in assessment_scores:
                    assessments_data.append({
                        "assessment_id": str(score.assessment.id),
                        "assessment_name": score.assessment.title,
                        "score": float(score.total_score),
                        "submitted_at": score.created_at
                    })
                    total_student_score += float(score.total_score)
                    assessment_count += 1
                
                average_score = (total_student_score / assessment_count) if assessment_count else 0
                
                students_data.append({
                    "student_id": str(enrollment.user.id),
                    "student_name": f"{enrollment.user.first_name} {enrollment.user.last_name}",
                    "progress": {
                        "completed_lectures": completed_lectures,
                        "total_lectures": total_lectures,
                        "completion_percentage": round(completion_percentage, 2)
                    },
                    "assessments": assessments_data,
                    "average_score": round(average_score, 2)
                })
                
                total_completion += completion_percentage
                total_score += average_score
                student_count += 1
            
            course_statistics = {
                "total_students": student_count,
                "average_completion": round(total_completion / student_count, 2) if student_count else 0,
                "average_score": round(total_score / student_count, 2) if student_count else 0
            }
            
            courses_data.append({
                "course_id": str(course.id),
                "course_name": course.name,
                "students": students_data,
                "course_statistics": course_statistics
            })
        
        return Response({"courses": courses_data})
