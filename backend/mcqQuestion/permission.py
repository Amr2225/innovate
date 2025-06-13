from rest_framework import permissions


class McqQuestionPermission(permissions.BasePermission):
    """Custom permission class for MCQ questions"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role in ["Teacher", "Institution"]

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            # Students can only view questions for their enrolled courses
            if user.role == "Student":
                return obj.assessment.course.enrollments.filter(user=user).exists()
            return True

        # Only creator or course instructor/institution can modify
        return (obj.created_by == user or
                obj.assessment.course.instructors.filter(id=user.id).exists() or
                obj.assessment.course.institution == user)
