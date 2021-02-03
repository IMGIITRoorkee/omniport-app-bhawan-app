from rest_framework import permissions
from formula_one.enums.active_status import ActiveStatus
from bhawan_app.managers.services import is_hostel_admin


class IsHostelAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow admin of an object to edit
    it.
    """

    def has_permission(self, request, view):
        """
        Returns if the authenticated user has the permissions to access a
        particular object
        :param obj: an instance of the bhawan app models whose permissions is
        checked
        :return: if the the person is allowed or not
        """
        hostel_code=request.parser_context['kwargs']['hostel__code']
        return is_hostel_admin(request.user.person, hostel_code)