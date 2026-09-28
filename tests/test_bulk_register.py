import datetime

import swapper
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from base_auth.models import User
from bhawan_app.constants import designations, statuses
from bhawan_app.models import HostelAdmin, Resident

Person = swapper.load_model('kernel', 'Person')
Student = swapper.load_model('kernel', 'Student')
Branch = swapper.load_model('kernel', 'Branch')
Degree = swapper.load_model('kernel', 'Degree')
Department = swapper.load_model('kernel', 'Department')
Residence = swapper.load_model('kernel', 'Residence')

URL = '/api/bhawan_app/rjb/resident/bulk_register/'


def make_row(row_number=2, **values):
    """
    Builds a row the way the bulk register page sends it, with every key present
    """

    row = {
        'row_number': row_number,
        'enrolment_number': '21114002',
        'hostel_code': 'rjb',
        'room_no': 'A-101',
        'seat': '',
        'fee_type': '',
        'admission_date': '',
        'mobile_no': '',
        'address': '',
        'father_name': '',
        'father_contact': '',
        'mother_name': '',
        'mother_contact': '',
    }
    row.update(values)
    return row


class BulkRegisterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rjb = Residence.objects.create(code='rjb')
        cls.rkb = Residence.objects.create(code='rkb')
        department = Department.objects.create(code='ased')
        branch = Branch.objects.create(
            entity_content_type=ContentType.objects.get_for_model(Department),
            entity_object_id=department.id,
            code='CSE',
            name='Computer Science',
            degree=Degree.objects.create(code='btech'),
            semester_count=8,
            year_count=4,
        )

        cls.supervisor = cls.make_admin('rjbsup', designations.SUPERVISOR, cls.rjb)
        cls.dosw = cls.make_admin('dosw', designations.DOSW, None)

        cls.mover, cls.newcomer = (
            Student.objects.create(
                person=Person.objects.create(full_name=full_name),
                enrolment_number=enrolment_number,
                branch=branch,
                current_semester=3,
                start_date=datetime.date(2021, 7, 20),
            )
            for enrolment_number, full_name in (('21114001', 'Kernel Name'), ('21114002', 'Diya Patel'))
        )
        Resident.objects.create(
            person=cls.mover.person,
            hostel=cls.rkb,
            room_number='B-1',
            start_date=timezone.now(),
        )

    def setUp(self):
        # The last seen middleware records the user agent of every session.
        self.client.defaults['HTTP_USER_AGENT'] = 'bulk-register-tests'

    @staticmethod
    def make_admin(username, designation, hostel):
        person = Person.objects.create(
            user=User.objects.create_user(username=username, password='x'),
            full_name=username,
        )
        HostelAdmin.objects.create(person=person, designation=designation, hostel=hostel)
        return person

    def post(self, rows, dry_run=False, as_person=None):
        self.client.force_login((as_person or self.supervisor).user)
        return self.client.post(
            URL,
            {'dry_run': dry_run, 'rows': rows},
            content_type='application/json',
        )

    def report_row(self, response, index=0):
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()['rows'][index]

    def active_hostels(self, student):
        return list(
            Resident.objects.filter(person=student.person, is_resident=True).values_list('hostel__code', flat=True)
        )

    def test_dry_run_reports_the_real_actions_and_writes_nothing(self):
        response = self.post([make_row(), make_row(3, enrolment_number='21114001')], dry_run=True)

        body = response.json()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIs(body['dry_run'], True)
        self.assertEqual(body['summary'], {'created': 2, 'updated': 0, 'existing': 0, 'skipped': 0})
        self.assertEqual(
            [(row['row_number'], row['enrolment_number'], row['action'], row['status']) for row in body['rows']],
            [(2, '21114002', 'would_create', 'dry_run'), (3, '21114001', 'would_create', 'dry_run')],
        )
        self.assertEqual(self.active_hostels(self.newcomer), [])
        self.assertEqual(self.active_hostels(self.mover), ['rkb'])

    def test_missing_dry_run_flag_defaults_to_a_dry_run(self):
        self.client.force_login(self.supervisor.user)
        response = self.client.post(URL, {'rows': [make_row()]}, content_type='application/json')

        self.assertEqual(self.report_row(response)['action'], 'would_create')
        self.assertEqual(self.active_hostels(self.newcomer), [])

    def test_student_not_on_channeli_is_skipped_and_reported(self):
        body = self.post([make_row(2, enrolment_number='26114001'), make_row(3)]).json()

        self.assertEqual(body['summary'], {'created': 1, 'updated': 0, 'existing': 0, 'skipped': 1})
        self.assertEqual(body['rows'][0], {
            'row_number': 2,
            'enrolment_number': '26114001',
            'action': 'skipped',
            'status': 'error',
            'message': 'Enrollment No 26114001 is not a student on Channeli',
        })
        self.assertFalse(Student.objects.filter(enrolment_number='26114001').exists())
        self.assertFalse(User.objects.filter(username='26114001').exists())
        self.assertEqual(self.active_hostels(self.newcomer), ['rjb'])

    def test_row_values_are_stored_on_the_residency_only(self):
        row = self.report_row(self.post([make_row(
            full_name='Changed Name',
            current_semester='5',
            seat='A',
            fee_type=statuses.NOT_LIVING,
            admission_date='2026-07-20',
            mobile_no='9876543210',
            address='12 MG Road, Jaipur',
            father_name='Rakesh Patel',
            father_contact='9876500000',
            mother_name='Sunita Patel',
            mother_contact='9876511111',
        )]))

        self.assertEqual((row['action'], row['status'], row['message']), ('created', 'success', ''))
        resident = Resident.objects.get(person=self.newcomer.person)
        self.assertEqual(
            (resident.hostel, resident.room_number, resident.fee_type, resident.is_resident),
            (self.rjb, 'A-101-A', statuses.NOT_LIVING, True),
        )
        self.assertEqual(timezone.localtime(resident.admission_date).date(), datetime.date(2026, 7, 20))
        self.assertEqual(
            (resident.address_bhawan, resident.contact_number_as_bhawan),
            ('12 MG Road, Jaipur', '9876543210'),
        )
        self.assertEqual(
            (resident.father.full_name, resident.fathers_contact, resident.mother.full_name, resident.mothers_contact),
            ('Rakesh Patel', '9876500000', 'Sunita Patel', '9876511111'),
        )
        self.newcomer.refresh_from_db()
        self.assertEqual((self.newcomer.person.full_name, self.newcomer.current_semester), ('Diya Patel', 3))

    def test_empty_optional_values_fall_back_to_defaults(self):
        self.post([make_row()])

        resident = Resident.objects.get(person=self.newcomer.person)
        self.assertEqual(
            (resident.room_number, resident.fee_type, resident.admission_date, resident.father),
            ('A-101', statuses.LIVING, None, None),
        )

    def test_student_moves_in_from_another_bhawan(self):
        row = self.report_row(self.post([make_row(enrolment_number='21114001')]))

        self.assertEqual((row['action'], row['message']), ('created', 'Moved from rkb'))
        old, new = Resident.objects.filter(person=self.mover.person).order_by('id')
        self.assertEqual((old.hostel, old.is_resident), (self.rkb, False))
        self.assertIsNotNone(old.end_date)
        self.assertEqual((new.hostel, new.is_resident), (self.rjb, True))

    def test_existing_residency_is_updated_in_place(self):
        row = make_row(admission_date='2026-07-20', father_name='Rakesh Patel', fee_type=statuses.NOT_LIVING)
        self.post([row])

        self.assertEqual(self.report_row(self.post([row]))['action'], 'existing')

        updated = self.report_row(self.post([dict(row, room_no='A-102', father_name='Rakesh K Patel', fee_type='')]))
        self.assertEqual(updated['action'], 'updated')
        resident = Resident.objects.get(person=self.newcomer.person)
        self.assertEqual(
            (resident.room_number, resident.father.full_name, resident.fee_type),
            ('A-102', 'Rakesh K Patel', statuses.NOT_LIVING),
        )

    def test_ending_a_stray_residency_counts_as_an_update(self):
        Resident.objects.create(
            person=self.mover.person,
            hostel=self.rjb,
            room_number='A-101',
            start_date=timezone.now(),
        )

        row = self.report_row(self.post([make_row(enrolment_number='21114001')]))

        self.assertEqual((row['action'], row['message']), ('updated', 'Moved from rkb'))
        self.assertEqual(self.active_hostels(self.mover), ['rjb'])

    def test_a_bad_row_is_skipped_without_blocking_the_others(self):
        body = self.post([
            make_row(2),
            make_row(3),
            make_row(4, enrolment_number='21114003', fee_type='xyz'),
            make_row(5, enrolment_number='21114001', seat='WINGSIDE'),
            make_row(6, enrolment_number='2111400'),
        ]).json()

        self.assertEqual(body['summary'], {'created': 1, 'updated': 0, 'existing': 0, 'skipped': 4})
        messages = {row['row_number']: row['message'] for row in body['rows'] if row['status'] == 'error'}
        self.assertEqual(messages[3], 'Enrollment No 21114002 is repeated from row 2')
        self.assertTrue(messages[4].startswith('fee_type: '), messages[4])
        self.assertTrue(
            messages[5].startswith('room_number: Ensure this value has at most 10 characters'),
            messages[5],
        )
        self.assertTrue(messages[6].startswith('enrolment_number: '), messages[6])
        self.assertEqual(self.active_hostels(self.newcomer), ['rjb'])
        self.assertEqual(self.active_hostels(self.mover), ['rkb'])

    def test_supervisor_cannot_register_into_another_bhawan(self):
        row = self.report_row(self.post([make_row(hostel_code='rkb')]))

        self.assertEqual(row['message'], 'You cannot register residents in rkb')
        self.assertEqual(self.active_hostels(self.newcomer), [])

    def test_unknown_bhawan_is_reported(self):
        row = self.report_row(self.post([make_row(hostel_code='xyz')]))

        self.assertTrue(row['message'].startswith('hostel_code: '), row['message'])

    def test_global_admin_can_register_into_any_bhawan(self):
        row = self.report_row(self.post([make_row(hostel_code='rkb')], as_person=self.dosw))

        self.assertEqual(row['action'], 'created')
        self.assertEqual(self.active_hostels(self.newcomer), ['rkb'])

    def test_non_admin_is_forbidden(self):
        outsider = Person.objects.create(
            user=User.objects.create_user(username='outsider', password='x'),
            full_name='Outsider',
        )

        response = self.post([make_row()], as_person=outsider)

        self.assertEqual(response.status_code, 403)
        self.assertIn('detail', response.json())

    def test_rows_must_be_a_non_empty_list_of_objects(self):
        for rows in ([], 'rows', ['row']):
            response = self.post(rows)
            self.assertEqual(response.status_code, 400, rows)
            self.assertIn('detail', response.json())
