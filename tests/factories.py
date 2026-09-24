import itertools

import swapper
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from bhawan_app.constants import designations
from bhawan_app.models.roles import HostelAdmin

Person = swapper.load_model('kernel', 'Person')
Student = swapper.load_model('kernel', 'Student')
Branch = swapper.load_model('kernel', 'Branch')
Degree = swapper.load_model('kernel', 'Degree')
Department = swapper.load_model('kernel', 'Department')
Residence = swapper.load_model('kernel', 'Residence')

_sequence = itertools.count(1)


def create_residence(code):
    return Residence.objects.create(code=code)


def create_person(full_name=None):
    number = next(_sequence)
    user = get_user_model().objects.create(username=f'user{number}')
    return Person.objects.create(
        user=user,
        full_name=full_name or f'Person {number}',
    )


def _get_branch():
    department, _ = Department.objects.get_or_create(code='csed')
    degree, _ = Degree.objects.get_or_create(code='btech')
    branch, _ = Branch.objects.get_or_create(
        code='cse',
        defaults={
            'name': 'Computer Science',
            'degree': degree,
            'entity_content_type': ContentType.objects.get_for_model(Department),
            'entity_object_id': department.id,
        },
    )
    return branch


def create_student(full_name=None):
    person = create_person(full_name)
    Student.objects.create(
        person=person,
        branch=_get_branch(),
        enrolment_number=f'{19114000 + person.id}',
        current_year=2,
        current_semester=3,
        start_date='2024-07-01',
    )
    return person


def create_hostel_admin(hostel, designation=designations.WARDEN):
    person = create_person()
    HostelAdmin.objects.create(
        person=person,
        designation=designation,
        hostel=hostel,
    )
    return person


def create_global_admin():
    person = create_person()
    HostelAdmin.objects.create(
        person=person,
        designation=designations.GLOBAL_COUNCIL_LIST[0],
    )
    return person


def client_for(person):
    client = APIClient()
    token = RefreshToken.for_user(person.user).access_token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client
