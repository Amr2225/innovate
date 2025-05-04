from rest_framework.permissions import BasePermission


class isInstitution(BasePermission):
    def has_permission(self, request, view):
        # return bool(request.user and request.user.is_authenticated and request.user.role == "Institution")
        if not request.user.is_authenticated:
            return False
        return request.user.role == "Institution"


class isStudent(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == "Student"


class isTeacher(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == "Teacher"
