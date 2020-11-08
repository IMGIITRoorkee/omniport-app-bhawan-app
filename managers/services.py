from formula_one.enums.active_status import ActiveStatus
from bhawan_app.models.roles import HostelAdmin
from bhawan_app.constants import designations


def get_hostel_admin(person, active_status=ActiveStatus.ANY):
    """
    Determines if the person has hostel administrator privileges
    :param person: an instance of the Person model whose roles are sought
    :param active_status: whether the role was, is, isn't or will be active
    :return: the role, if the person fulfills it
    """

    try:
        # queryset = HostelAdmin.objects.filter(active_status)
        role = HostelAdmin.objects.get(person=person)
        return role
    except HostelAdmin.DoesNotExist:
        return None


def is_supervisor(person):
    """
    Determines if the person has hostel supervisor privileges
    :param person: an instance of the Person model whose roles are sought
    :return: true if person is supervisor else false
    """

    role = get_hostel_admin(person)
    if role is not None:
        return role.designation == designations.SUPERVISOR
    return False

def is_warden(person):
    """
    Determines if the person has hostel Warden privileges
    :param person: an instance of the Person model whose roles are sought
    :return: true if person is Warden else false
    """

    role = get_hostel_admin(person)
    if role is not None:
        return role.designation == designations.WARDEN \
            or role.designation == designations.CHIEF_WARDEN \
            or role.designation == designations.ASSISTANT_WARDEN
    return False

def is_hostel_admin(person):
    """
    Returns if the person is hostel admin or not
    :param person: an instance of the Person model whose roles are sought
    :return: if the person is hostel admin or not
    """

    hostel_admin = get_hostel_admin(person)
    return hostel_admin is not None