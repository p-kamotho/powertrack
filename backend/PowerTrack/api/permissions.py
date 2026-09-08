from rest_framework.permissions import BasePermission


class IsAuthenticatedReadOnlyOrStaff(BasePermission):
    """
    Authenticated users may read API resources.
    Staff users may create, update, and delete resources.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return request.user.is_staff
