from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count, Max, Min
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore
from users.models import User

class StudentMetricsView(generics.GenericAPIView):
    """
    API endpoint for detailed student metrics.
    
    GET /api/teacher-analytics/student-metrics/ - Returns detailed metrics for the authenticated student
    
    Returns:
    {
        "student_id": "uuid",
        "student_name": "string",
        "overall_metrics": {
            "total_courses": integer,
            "completed_courses": integer,
            "average_grade": float,
            "total_lectures_completed": integer,
            "total_assessments_completed": integer
        },
        "course_metrics": [
            {
                "course_id": "uuid",
                "course_name": "string",
                "progress": {
                    "completed_lectures": integer,
                    "total_lectures": integer,
                    "completion_percentage": float,
                    "average_time_per_lecture": float
                },
                "assessment_performance": {
                    "total_assessments": integer,
                    "completed_assessments": integer,
                    "average_score": float,
                    "highest_score": float,
                    "lowest_score": float
                },
                "course_status": "string"  # "completed", "in_progress", "not_started"
            }
        ],
        "performance_trend": {
            "average_scores": [
                {
                    "date": "YYYY-MM-DD",
                    "score": float
                }
            ],
            "completion_rate": [
                {
                    "date": "YYYY-MM-DD",
                    "percentage": float
                }
            ]
        }
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the authenticated user
        student = request.user

        # Get all enrollments for the student
        enrollments = Enrollments.objects.filter(user=student)
        courses = Course.objects.filter(enrollments__in=enrollments)

        # Calculate overall metrics
        total_courses = courses.count()
        
        # Get all assessment scores
        assessment_scores = AssessmentScore.objects.filter(enrollment__in=enrollments)
        total_assessments_completed = assessment_scores.count()
        
        # Calculate average grade
        average_grade = assessment_scores.aggregate(avg=Avg('total_score'))['avg'] or 0
        
        # Get total lectures completed
        total_lectures_completed = LectureProgress.objects.filter(
            enrollment__in=enrollments,
            completed=True
        ).count()

        # Calculate course-specific metrics
        course_metrics = []
        completed_courses_count = 0
        
        for course in courses:
            enrollment = enrollments.get(course=course)
            
            # Get lecture progress
            lectures = Lecture.objects.filter(chapter__course=course)
            total_lectures = lectures.count()
            completed_lectures = LectureProgress.objects.filter(
                enrollment=enrollment,
                completed=True
            ).count()
            
            # Calculate average time per lecture
            lecture_times = LectureProgress.objects.filter(
                enrollment=enrollment,
                completed=True
            ).values_list('time_spent', flat=True)
            avg_time = sum(lecture_times) / len(lecture_times) if lecture_times else 0
            
            # Get assessment performance
            course_assessments = Assessment.objects.filter(course=course)
            total_assessments = course_assessments.count()
            course_scores = AssessmentScore.objects.filter(
                enrollment=enrollment,
                assessment__in=course_assessments
            )
            
            completed_assessments = course_scores.count()
            
            # Calculate assessment scores
            if completed_assessments > 0:
                avg_score = course_scores.aggregate(avg=Avg('total_score'))['avg'] or 0
                highest_score = course_scores.aggregate(max=Max('total_score'))['max'] or 0
                lowest_score = course_scores.aggregate(min=Min('total_score'))['min'] or 0
            else:
                avg_score = 0
                highest_score = 0
                lowest_score = 0
            
            # Determine course status
            if completed_lectures == total_lectures and completed_assessments == total_assessments:
                course_status = "completed"
                completed_courses_count += 1
            elif completed_lectures > 0 or completed_assessments > 0:
                course_status = "in_progress"
            else:
                course_status = "not_started"
            
            course_metric = {
                "course_id": str(course.id),
                "course_name": course.name,
                "progress": {
                    "completed_lectures": completed_lectures,
                    "total_lectures": total_lectures,
                    "completion_percentage": round((completed_lectures / total_lectures * 100) if total_lectures > 0 else 0, 2),
                    "average_time_per_lecture": round(float(avg_time), 2)
                },
                "assessment_performance": {
                    "total_assessments": total_assessments,
                    "completed_assessments": completed_assessments,
                    "average_score": round(float(avg_score), 2),
                    "highest_score": round(float(highest_score), 2),
                    "lowest_score": round(float(lowest_score), 2)
                },
                "course_status": course_status
            }
            
            course_metrics.append(course_metric)

        # Prepare response data
        response_data = {
            "student_id": str(student.id),
            "student_name": f"{student.full_name}",
            "overall_metrics": {
                "total_courses": total_courses,
                "completed_courses": completed_courses_count,  # Use the count from course status
                "average_grade": round(float(average_grade), 2),
                "total_lectures_completed": total_lectures_completed,
                "total_assessments_completed": total_assessments_completed
            },
            "course_metrics": course_metrics,
            "performance_trend": {
                "average_scores": [],  # This would require historical data
                "completion_rate": []  # This would require historical data
            }
        }

        return Response(response_data) 