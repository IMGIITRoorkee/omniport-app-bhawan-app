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


class ResidentRegistrationTests(APITestCase):
    def setUp(self):
        self.hostel = create_residence('azb')
        self.other_hostel = create_residence('gnb')
        self.warden = client_for(create_hostel_admin(self.hostel))
        self.other_warden = client_for(create_hostel_admin(self.other_hostel))
        self.student = create_student()

    def register(self, client, hostel, person):
        return client.post(
            f'/api/bhawan_app/{hostel.code}/resident/',
            {
                'person': person.id,
                'room_number': 'A-101',
                'start_date': '2026-07-01T00:00:00',
                'fee_type': statuses.LIVING,
                'address_bhawan': '',
                'admission_date': '',
                'contact_number_as_bhawan': '9999999999',
            },
            format='json',
        )

    def retrieve(self, client, hostel, person):
        enrolment_number = person.student.enrolment_number
        return client.get(
            f'/api/bhawan_app/{hostel.code}/resident/{enrolment_number}/'
        )

    def active_residencies(self, person):
        return Resident.objects.filter(person=person, is_resident=True)

    def test_registers_new_student(self):
        response = self.register(self.warden, self.hostel, self.student)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        residency = self.active_residencies(self.student).get()
        self.assertEqual(residency.hostel, self.hostel)

    def test_rejects_second_registration_in_same_bhawan(self):
        self.register(self.warden, self.hostel, self.student)

        response = self.register(self.warden, self.hostel, self.student)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.json(),
            'Student is already registered in this bhawan.',
        )
        self.assertEqual(self.active_residencies(self.student).count(), 1)

    def test_registering_in_another_bhawan_transfers_the_student(self):
        self.register(self.warden, self.hostel, self.student)

        response = self.register(self.other_warden, self.other_hostel, self.student)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        residency = self.active_residencies(self.student).get()
        self.assertEqual(residency.hostel, self.other_hostel)
        previous = Resident.objects.get(
            person=self.student,
            hostel=self.hostel,
        )
        self.assertFalse(previous.is_resident)
        self.assertIsNotNone(previous.end_date)

    def test_can_register_again_after_leaving(self):
        self.register(self.warden, self.hostel, self.student)
        self.active_residencies(self.student).update(is_resident=False)

        response = self.register(self.warden, self.hostel, self.student)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.active_residencies(self.student).count(), 1)

    def test_retrieve_reports_resident_status_to_the_frontend(self):
        response = self.retrieve(self.warden, self.hostel, self.student)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.json()['isResident'], False)

        self.register(self.warden, self.hostel, self.student)

        response = self.retrieve(self.warden, self.hostel, self.student)
        self.assertIs(response.json()['isResident'], True)

        response = self.retrieve(self.other_warden, self.other_hostel, self.student)
        self.assertIs(response.json()['isResident'], False)
