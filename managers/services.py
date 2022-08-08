from formula_one.enums.active_status import ActiveStatus
from bhawan_app.models.roles import HostelAdmin
from bhawan_app.constants import designations

from kernel.managers.get_role import get_role

def get_hostel_admin(person, hostel_code, active_status=ActiveStatus.ANY):
    """
    Determines if the person has hostel administrator privileges
    :param person: an instance of the Person model whose roles are sought
    :param active_status: whether the role was, is, isn't or will be active
    :return: the role, if the person fulfills it
    """

    try:
        role = HostelAdmin.objects.get(person=person, hostel__code=hostel_code)
        return role
    except HostelAdmin.DoesNotExist:
        return None

def is_global_admin(person):
    """
    Determine if the person has the global administrative priviliges
    """
    return HostelAdmin.objects.filter(person=person, designation__in=designations.GLOBAL_COUNCIL_LIST).first()

def is_supervisor(person, hostel_code):
    """
    Determines if the person has hostel supervisor privileges
    :param person: an instance of the Person model whose roles are sought
    :return: true if person is supervisor else false
    """

    role = get_hostel_admin(person, hostel_code)
    if role is not None:
        return role.designation == designations.SUPERVISOR
    return False

def is_warden(person, hostel_code):
    """
    Determines if the person has hostel Warden privileges
    :param person: an instance of the Person model whose roles are sought
    :return: true if person is Warden else false
    """

    role = get_hostel_admin(person, hostel_code)
    if role is not None:
        return role.designation == designations.WARDEN \
            or role.designation == designations.CHIEF_WARDEN \
            or role.designation == designations.ASSISTANT_WARDEN
    return False

def is_hostel_admin(person, hostel_code):
    """
    Returns if the person is hostel admin or not
    :param person: an instance of the Person model whose roles are sought
    :return: if the person is hostel admin or not
    """

    hostel_admin = get_hostel_admin(person, hostel_code)
    return hostel_admin is not None

def is_senior_maintainer(person):
    """
    Returns if the person is a senior maintainer or not
    :param person: an instance of the Person model whose roles are sought
    :return: if the person is senior maintainer or not
    """

    maintainer = get_role(
            person=person,
            role_name='Maintainer',
            active_status=ActiveStatus.IS_ACTIVE,
            silent=True,
        )
    if maintainer:
        return person.student.current_semester > 4
    return False