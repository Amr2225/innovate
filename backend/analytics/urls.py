from django.urls import path
from .teacher_analytics_view import TeacherAnalyticsView
from .student_analytics_view import StudentAnalyticsView
from .top_students_view import TopStudentsView
from .course_metrics_view import CourseMetricsView
from .courses_metrics_view import TeacherCoursesMetricsView
from .student_metrics_view import StudentMetricsView
from .Student_Dashboard import CourseCountView
from .Course_Progress import CourseLectureProgressView
from .Student_Dashboard import StudentDashboardView

urlpatterns = [
    path('', TeacherAnalyticsView.as_view(), name='teacher-analytics'),
    path('students/', StudentAnalyticsView.as_view(), name='student-analytics'),
    path('students/<uuid:course_id>/', StudentAnalyticsView.as_view(),
         name='student-analytics-by-course'),
    path('top-students/<uuid:course_id>/',
         TopStudentsView.as_view(), name='top-students'),
    path('course-metrics/<uuid:course_id>/',
         CourseMetricsView.as_view(), name='course-metrics'),
    path('courses-metrics/', TeacherCoursesMetricsView.as_view(),
         name='courses-metrics'),
    path('student-metrics/', StudentMetricsView.as_view(), name='student-metrics'),
    path('course-count/', CourseCountView.as_view(), name='course-count'),
    path('lecture-progress/<uuid:course_id>/',
         CourseLectureProgressView.as_view(), name='lecture-progress'),
    path('student-dashboard/', StudentDashboardView.as_view(),
         name='student-dashboard'),
]
