from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore

class CourseMetricsView(generics.GenericAPIView):
    """
    API endpoint for course metrics.
    
    GET /api/teacher-analytics/course-metrics/{course_id}/ - Returns detailed metrics for a specific course
    
    Returns:
    {
        "course_id": "uuid",
        "course_name": "string",
        "enrollment_metrics": {
            "total_enrollments": integer,
            "active_enrollments": integer,
            "completion_rate": float,
            "dropout_rate": float,
            "average_enrollment_duration": float
        },
        "assessment_metrics": {
            "total_assessments": integer,
            "assessment_types": {
                "exam": integer,
                "assignment": integer,
                "quiz": integer
            },
            "submission_rate": float,
            "average_grading_time": float
        },
        "performance_metrics": {
            "overall_average": float,
            "median_score": float,
            "standard_deviation": float,
            "passing_rate": float,
            "excellence_rate": float
        },
        "engagement_metrics": {
            "average_completion_time": float,
            "active_students_percentage": float,
            "average_attempts_per_assessment": float,
            "most_attempted_assessment": string
        },
        "trend_metrics": {
            "enrollment_trend": [
                {
                    "date": "YYYY-MM-DD",
                    "count": integer
                }
            ],
            "performance_trend": [
                {
                    "date": "YYYY-MM-DD",
                    "average_score": float
                }
            ]
        }
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        if request.user.role != "Teacher":
            return Response(
                {"detail": "Only teachers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            course = Course.objects.get(id=course_id, instructors=request.user)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found or you don't have permission to access it"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all enrollments for the course
        enrollments = Enrollments.objects.filter(course=course)
        total_enrollments = enrollments.count()
        active_enrollments = enrollments.filter(is_completed=False).count()
        completed_enrollments = enrollments.filter(is_completed=True).count()

        # Calculate enrollment metrics
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        dropout_rate = 100 - completion_rate

        # Get assessment data
        assessments = Assessment.objects.filter(course=course)
        total_assessments = assessments.count()
        
        # Calculate assessment type distribution
        assessment_types = {
            'exam': assessments.filter(type='Exam').count(),
            'assignment': assessments.filter(type='Assignment').count(),
            'quiz': assessments.filter(type='Quiz').count()
        }

        # Get all assessment scores
        assessment_scores = AssessmentScore.objects.filter(
            assessment__course=course
        )

        # Calculate performance metrics
        scores = [float(score.total_score) for score in assessment_scores]
        overall_average = sum(scores) / len(scores) if scores else 0
        
        # Calculate median score
        sorted_scores = sorted(scores)
        mid = len(sorted_scores) // 2
        median_score = (sorted_scores[mid] + sorted_scores[~mid]) / 2 if sorted_scores else 0

        # Calculate standard deviation
        if scores:
            mean = sum(scores) / len(scores)
            squared_diff_sum = sum((x - mean) ** 2 for x in scores)
            standard_deviation = (squared_diff_sum / len(scores)) ** 0.5
        else:
            standard_deviation = 0

        # Calculate passing and excellence rates
        passing_threshold = 60  # 60% is considered passing
        excellence_threshold = 85  # 85% is considered excellent
        
        passing_count = sum(1 for score in scores if score >= passing_threshold)
        excellence_count = sum(1 for score in scores if score >= excellence_threshold)
        
        passing_rate = (passing_count / len(scores) * 100) if scores else 0
        excellence_rate = (excellence_count / len(scores) * 100) if scores else 0

        # Calculate engagement metrics
        lecture_progress = LectureProgress.objects.filter(
            enrollment__course=course
        )
        
        total_lectures = Lecture.objects.filter(chapter__course=course).count()
        completed_lectures = lecture_progress.filter(completed=True).count()
        
        average_completion_time = lecture_progress.aggregate(
            avg_time=Avg('time_spent')
        )['avg_time'] or 0

        active_students_percentage = (active_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0

        # Calculate average attempts per assessment
        total_attempts = assessment_scores.count()
        average_attempts = (total_attempts / total_assessments) if total_assessments > 0 else 0

        # Find most attempted assessment
        most_attempted = assessment_scores.values('assessment__title').annotate(
            attempt_count=Count('id')
        ).order_by('-attempt_count').first()
        
        most_attempted_assessment = most_attempted['assessment__title'] if most_attempted else "No attempts"

        # Prepare response data
        response_data = {
            "course_id": str(course.id),
            "course_name": course.name,
            "enrollment_metrics": {
                "total_enrollments": total_enrollments,
                "active_enrollments": active_enrollments,
                "completion_rate": round(completion_rate, 2),
                "dropout_rate": round(dropout_rate, 2),
                "average_enrollment_duration": 0  # This would require additional tracking
            },
            "assessment_metrics": {
                "total_assessments": total_assessments,
                "assessment_types": assessment_types,
                "submission_rate": round((total_attempts / (total_enrollments * total_assessments) * 100) if total_assessments > 0 else 0, 2),
                "average_grading_time": 0  # This would require additional tracking
            },
            "performance_metrics": {
                "overall_average": round(overall_average, 2),
                "median_score": round(median_score, 2),
                "standard_deviation": round(standard_deviation, 2),
                "passing_rate": round(passing_rate, 2),
                "excellence_rate": round(excellence_rate, 2)
            },
            "engagement_metrics": {
                "average_completion_time": round(float(average_completion_time), 2),
                "active_students_percentage": round(active_students_percentage, 2),
                "average_attempts_per_assessment": round(average_attempts, 2),
                "most_attempted_assessment": most_attempted_assessment
            },
            "trend_metrics": {
                "enrollment_trend": [],  # This would require historical data
                "performance_trend": []  # This would require historical data
            }
        }

        return Response(response_data) 