from rest_framework import permissions
from bhawan_app.managers.services import is_hostel_admin
from bhawan_app.constants import designations

class IsSupervisor(permissions.BasePermission):
    """
    Permission to only allow supervisors to interact with the object.
    """

    def has_permission(self, request, view):
        """
        Returns if the authenticated user has the permissions to access a
        particular object
        :param obj: an instance of the bhawan app models whose permissions is
        checked
        :return: if the the person is allowed or not
        """
        person = request.person
        hostel_code=request.parser_context['kwargs']['hostel__code']
        if is_hostel_admin(person, hostel_code):
            return person.hosteladmin.designation == designations.SUPERVISOR
        return False