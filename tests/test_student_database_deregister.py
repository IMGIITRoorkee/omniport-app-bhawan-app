import swapper
from rest_framework import status
from rest_framework.test import APITestCase

from bhawan_app.constants import statuses
from bhawan_app.models import Resident
from bhawan_app.tests.factories import (
    client_for,
    create_hostel_admin,
    create_residence,
    create_student,
)

Student = swapper.load_model('kernel', 'Student')


class StudentDatabaseDeregisterTests(APITestCase):
    """
    A student whose Student role has ended is hidden from the student search,
    so the Student Database list must give the frontend what it needs to
    deregister them.
    """

    def setUp(self):
        self.hostel = create_residence('azb')
        self.warden = client_for(create_hostel_admin(self.hostel))
        self.student = create_student()
        Resident.objects.create(
            person=self.student,
            hostel=self.hostel,
            room_number='A-101',
            fee_type=statuses.LIVING,
            start_date='2024-07-01T00:00:00',
        )
        Student.objects.filter(person=self.student).update(end_date='2025-06-30')

    def test_list_includes_person_id_of_student_with_ended_role(self):
        response = self.warden.get(
            f'/api/bhawan_app/{self.hostel.code}/resident/?is_student=true'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()['results']
        self.assertEqual([r['person'] for r in results], [self.student.id])

    def test_person_id_from_list_deregisters_the_student(self):
        person_id = self.warden.get(
            f'/api/bhawan_app/{self.hostel.code}/resident/?is_student=true'
        ).json()['results'][0]['person']

        response = self.warden.get(
            f'/api/bhawan_app/{self.hostel.code}/resident/{person_id}/deregister/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        residency = Resident.objects.get(person=self.student)
        self.assertFalse(residency.is_resident)
        self.assertIsNotNone(residency.end_date)
