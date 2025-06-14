from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from assessment.models import AssessmentScore

class TeacherCoursesMetricsView(generics.GenericAPIView):
    """
    API endpoint for teacher courses metrics.

    GET /api/teacher-analytics/courses-metrics/ - Returns metrics for all courses taught by the teacher or institution
    
    Returns:
    {
        "courses": [
            {
                "course_id": "uuid",
                "course_name": "string",
                "progress_metrics": {
                    "total_students": integer,
                    "total_lectures": integer,
                    "average_progress": float,
                    "completion_rate": float
                },
                "assessment_metrics": {
                    "total_assessments": integer,
                    "average_score": float,
                    "submission_rate": float
                },
                "student_metrics": {
                    "active_students": integer,
                    "completed_course": integer,
                    "in_progress": integer
                }
            }
        ],
        "overall_metrics": {
            "total_courses": integer,
            "total_students": integer,
            "average_completion_rate": float,
            "average_assessment_score": float
        }
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == "Teacher":
            courses = Course.objects.filter(instructors=user)
        elif user.role == "Institution":
            courses = Course.objects.filter(institution=user)
        else:
            return Response(
                {"detail": "Only teachers and institutions can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        courses_data = []
        total_completion_rate = 0
        total_assessment_score = 0
        
        all_enrollments = Enrollments.objects.filter(course__in=courses)
        unique_students = all_enrollments.values('user').distinct().count()
        
        for course in courses:
            enrollments = Enrollments.objects.filter(course=course)
            lectures = Lecture.objects.filter(chapter__course=course)
            assessments = course.assessments.all()
            
            total_course_students = enrollments.count()
            total_course_lectures = lectures.count()
            
            completed_lectures = LectureProgress.objects.filter(
                enrollment__in=enrollments,
                completed=True
            ).count()
            
            total_possible_completions = total_course_students * total_course_lectures
            average_progress = (completed_lectures / total_possible_completions * 100) if total_possible_completions > 0 else 0
            
            total_assessments = assessments.count()
            assessment_scores = AssessmentScore.objects.filter(
                assessment__in=assessments,
                enrollment__in=enrollments
            )
            
            avg_score = assessment_scores.aggregate(avg=Avg('total_score'))['avg'] or 0
            submission_rate = (assessment_scores.count() / (total_course_students * total_assessments) * 100) if total_assessments > 0 else 0
            
            active_students = enrollments.filter(is_completed=False).count()
            completed_course = enrollments.filter(is_completed=True).count()
            
            student_progress = {
                "completed_all": 0,
                "in_progress": 0,
                "not_started": 0
            }
            
            for enrollment in enrollments:
                completed_lectures_count = LectureProgress.objects.filter(
                    enrollment=enrollment,
                    completed=True
                ).count()
                
                if completed_lectures_count == total_course_lectures:
                    student_progress["completed_all"] += 1
                elif completed_lectures_count > 0:
                    student_progress["in_progress"] += 1
                else:
                    student_progress["not_started"] += 1
            
            course_data = {
                "course_id": str(course.id),
                "course_name": course.name,
                "progress_metrics": {
                    "total_students": total_course_students,
                    "total_lectures": total_course_lectures,
                    "average_progress": round(average_progress, 2),
                    "completion_rate": round((student_progress["completed_all"] / total_course_students * 100) if total_course_students > 0 else 0, 2)
                },
                "assessment_metrics": {
                    "total_assessments": total_assessments,
                    "average_score": round(float(avg_score), 2),
                    "submission_rate": round(submission_rate, 2)
                },
                "student_metrics": {
                    "active_students": active_students,
                    "completed_course": completed_course,
                    "in_progress": student_progress["in_progress"]
                }
            }
            
            courses_data.append(course_data)
            
            total_completion_rate += course_data["progress_metrics"]["completion_rate"]
            total_assessment_score += course_data["assessment_metrics"]["average_score"]
        
        total_courses = len(courses)
        overall_metrics = {
            "total_courses": total_courses,
            "total_students": unique_students,
            "average_completion_rate": round(total_completion_rate / total_courses, 2) if total_courses > 0 else 0,
            "average_assessment_score": round(total_assessment_score / total_courses, 2) if total_courses > 0 else 0
        }
        
        response_data = {
            "courses": courses_data,
            "overall_metrics": overall_metrics
        }
        
        return Response(response_data)
