import csv
import io

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from bhawan_app.constants import designations
from bhawan_app.models import NonResidingStudent
from bhawan_app.tests.factories import (
    client_for,
    create_global_admin,
    create_hostel_admin,
    create_person,
    create_residence,
)


def payload(**overrides):
    data = {
        'name': 'Asha Verma',
        'designation': NonResidingStudent.JRF,
        'department': 'csed',
        'mobile_number': '9876543210',
        'room_number': 'B-12',
        'from_date': '2026-08-01',
        'upto_date': '2026-12-31',
        'email_id': 'asha@example.org',
    }
    data.update(overrides)
    return data


class NonResidingStudentTests(APITestCase):
    def setUp(self):
        self.hostel = create_residence('azb')
        self.other_hostel = create_residence('gnb')
        self.warden = client_for(create_hostel_admin(self.hostel))
        self.supervisor = client_for(
            create_hostel_admin(self.hostel, designations.SUPERVISOR)
        )
        self.other_warden = client_for(create_hostel_admin(self.other_hostel))
        self.global_admin = client_for(create_global_admin())
        self.outsider = client_for(create_person())

    def url(self, hostel, suffix=''):
        return f'/api/bhawan_app/{hostel.code}/non_residing_student/{suffix}'

    def add(self, hostel, **overrides):
        return NonResidingStudent.objects.create(
            hostel=hostel,
            **{
                **payload(),
                'from_date': '2026-08-01',
                'upto_date': '2026-12-31',
                **overrides,
            },
        )

    def test_warden_registers_nrs_in_own_bhawan(self):
        response = self.warden.post(self.url(self.hostel), payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['hostelCode'], 'azb')
        self.assertEqual(NonResidingStudent.objects.get().hostel, self.hostel)

    def test_supervisor_can_register(self):
        response = self.supervisor.post(self.url(self.hostel), payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_hostel_comes_from_the_url_not_the_payload(self):
        response = self.warden.post(
            self.url(self.hostel),
            payload(hostel=self.other_hostel.id),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NonResidingStudent.objects.get().hostel, self.hostel)

    def test_department_is_optional(self):
        response = self.warden.post(
            self.url(self.hostel),
            payload(department=''),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rejects_from_date_not_before_upto_date(self):
        for upto_date in ['2026-08-01', '2026-07-01']:
            with self.subTest(upto_date=upto_date):
                response = self.warden.post(
                    self.url(self.hostel),
                    payload(upto_date=upto_date),
                    format='json',
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(
                    'From date must be earlier than end date',
                    str(response.json()),
                )
        self.assertFalse(NonResidingStudent.objects.exists())

    def test_rejects_unknown_designation(self):
        response = self.warden.post(
            self.url(self.hostel),
            payload(designation='professor'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_register_in_another_bhawan(self):
        response = self.other_warden.post(self.url(self.hostel), payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(NonResidingStudent.objects.exists())

    def test_person_without_hostel_role_cannot_register(self):
        response = self.outsider.post(self.url(self.hostel), payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_request_is_rejected(self):
        response = APIClient().get(self.url(self.hostel))

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_list_is_scoped_to_the_bhawan_in_the_url(self):
        own = self.add(self.hostel, name='Own')
        self.add(self.other_hostel, name='Other')

        response = self.warden.get(self.url(self.hostel))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.json()], [own.id])

    def test_listing_another_bhawan_returns_nothing(self):
        self.add(self.hostel)

        response = self.other_warden.get(self.url(self.hostel))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_warden_updates_record(self):
        record = self.add(self.hostel)

        response = self.warden.patch(
            self.url(self.hostel, f'{record.id}/'),
            {'room_number': 'C-7'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.room_number, 'C-7')

    def test_update_validates_against_stored_dates(self):
        record = self.add(self.hostel)

        response = self.warden.patch(
            self.url(self.hostel, f'{record.id}/'),
            {'upto_date': '2026-07-01'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_update_another_bhawans_record(self):
        record = self.add(self.hostel)

        response = self.other_warden.patch(
            self.url(self.hostel, f'{record.id}/'),
            {'room_number': 'C-7'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        record.refresh_from_db()
        self.assertEqual(record.room_number, 'B-12')

    def test_global_admin_updates_record_through_its_own_bhawan(self):
        record = self.add(self.other_hostel)

        response = self.global_admin.patch(
            self.url(self.other_hostel, f'{record.id}/'),
            {'room_number': 'C-7'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_shows_a_warden_only_their_own_bhawans(self):
        own = self.add(self.hostel, name='Own')
        self.add(self.other_hostel, name='Other')

        response = self.warden.get('/api/bhawan_app/non_residing_student/all/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.json()], [own.id])

    def test_all_shows_global_admin_every_bhawan(self):
        self.add(self.hostel)
        self.add(self.other_hostel)

        response = self.global_admin.get('/api/bhawan_app/non_residing_student/all/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(row['hostelCode'] for row in response.json()),
            ['azb', 'gnb'],
        )

    def test_all_is_forbidden_without_a_hostel_role(self):
        self.add(self.hostel)

        response = self.outsider.get('/api/bhawan_app/non_residing_student/all/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_download_returns_csv_of_own_bhawan(self):
        self.add(self.hostel, name='Own')
        self.add(self.other_hostel, name='Other')

        response = self.warden.get(self.url(self.hostel, 'download/'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('azb_non_residing_students.csv', response['Content-Disposition'])
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        self.assertEqual(rows[0][:3], ['Name of the bhawan', 'Name', 'Designation'])
        self.assertEqual([row[1] for row in rows[1:]], ['Own'])
        self.assertEqual(rows[1][2], 'JRF')

    def test_cannot_download_another_bhawan(self):
        response = self.other_warden.get(self.url(self.hostel, 'download/'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_is_logged_with_row_count(self):
        self.add(self.hostel)

        with self.assertLogs('bhawan_app.views.non_residing_student', 'INFO') as logs:
            self.warden.get(self.url(self.hostel))

        self.assertIn('read 1 non residing student records', logs.output[0])

    def test_all_is_logged_with_the_hostels_it_covers(self):
        self.add(self.hostel)

        with self.assertLogs('bhawan_app.views.non_residing_student', 'INFO') as logs:
            self.warden.get('/api/bhawan_app/non_residing_student/all/')

        self.assertIn('read 1 non residing student records covering azb', logs.output[0])

    def test_download_is_logged_with_row_count(self):
        self.add(self.hostel)

        with self.assertLogs('bhawan_app.views.non_residing_student', 'INFO') as logs:
            self.warden.get(self.url(self.hostel, 'download/'))

        self.assertIn('downloaded azb_non_residing_students.csv with 1 rows', logs.output[0])
