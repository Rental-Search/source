
from rest_framework import permissions

class TeamStaffDjangoModelPermissions(permissions.DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user
        if user:
            # we only check for Django Model Permissions for the team staff
            if user.is_staff and not user.is_superuser:
                return super(TeamStaffDjangoModelPermissions, self).has_permission(request, view)
            # we require authenticated user
            if user.is_authenticated():
                return True
        # disallow by default
        return False
