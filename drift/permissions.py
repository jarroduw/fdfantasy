from rest_framework import permissions

class IsTeamOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        # Write permissions are only allowed to the owner of the snippet.
        return obj.team.owner == request.user or request.user.is_superuser