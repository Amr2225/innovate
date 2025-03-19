from rest_framework.permissions import BasePermission


class isInstitution(BasePermission):
    def has_permission(self, request, view):
        # return bool(request.user and request.user.is_authenticated and request.user.role == "Institution")
        if not request.user.is_authenticated:
            return False
        return request.user.role == "Institution"
