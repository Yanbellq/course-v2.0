# apps/api/authentication/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    GET — дозволено всім
    POST/PUT/PATCH/DELETE — тільки operator
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        
        return user.role == "operator"
