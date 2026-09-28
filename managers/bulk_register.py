import datetime

import swapper
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from bhawan_app.managers.services import can_manage_residents
from bhawan_app.models import Resident
from bhawan_app.serializers.bulk_register import BulkRegisterRowSerializer

Person = swapper.load_model('kernel', 'Person')
Student = swapper.load_model('kernel', 'Student')

# Row keys copied onto the Resident, mapped to the field that stores them
RESIDENT_FIELDS = {
    'fee_type': 'fee_type',
    'address': 'address_bhawan',
    'mobile_no': 'contact_number_as_bhawan',
    'father_contact': 'fathers_contact',
    'mother_contact': 'mothers_contact',
}
# Row keys holding parent names, mapped to the Resident relation they fill
PARENT_FIELDS = {
    'father_name': 'father',
    'mother_name': 'mother',
}
# How a dry run names the action a real run would take
DRY_RUN_ACTIONS = {
    'created': 'would_create',
    'updated': 'would_update',
}


def register_residents(rows, dry_run, person):
    """
    Registers every row as a resident of its bhawan and reports what happened to each row
    A dry run does the same work and rolls it back, so its report matches the real run
    """

    summary = {'created': 0, 'updated': 0, 'existing': 0, 'skipped': 0}
    report = []
    first_row_numbers = {}
    with transaction.atomic():
        for row in rows:
            row_number = row.get('row_number')
            try:
                data = _validate_row(row, person, first_row_numbers)
                with transaction.atomic():
                    action, message = _register_row(data)
                summary[action] += 1
                status = 'dry_run' if dry_run else 'success'
                if dry_run:
                    action = DRY_RUN_ACTIONS.get(action, action)
            except (serializers.ValidationError, ValidationError, ValueError) as error:
                summary['skipped'] += 1
                action, status, message = 'skipped', 'error', _error_message(error)
            report.append({
                'row_number': row_number,
                'enrolment_number': row.get('enrolment_number'),
                'action': action,
                'status': status,
                'message': message,
            })
        if dry_run:
            transaction.set_rollback(True)
    return {'dry_run': dry_run, 'summary': summary, 'rows': report}


def _validate_row(row, person, first_row_numbers):
    serializer = BulkRegisterRowSerializer(
        data={key: value for key, value in row.items() if value != ''},
    )
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    enrolment_number = data['enrolment_number']
    if enrolment_number in first_row_numbers:
        raise ValueError(
            f'Enrollment No {enrolment_number} is repeated from row {first_row_numbers[enrolment_number]}'
        )
    first_row_numbers[enrolment_number] = row.get('row_number')

    if not can_manage_residents(person, data['hostel'].code):
        raise ValueError(f"You cannot register residents in {data['hostel'].code}")
    return data


def _register_row(data):
    """
    Makes a Channeli student an active resident of the row's bhawan, ending residencies elsewhere
    An active residency in the same bhawan is updated in place
    """

    student = Student.objects.select_related('person').filter(
        enrolment_number=data['enrolment_number'],
    ).first()
    if student is None:
        raise ValueError(f"Enrollment No {data['enrolment_number']} is not a student on Channeli")

    active_residents = list(Resident.objects.select_related('hostel', 'father', 'mother').filter(
        person=student.person,
        is_resident=True,
    ))
    resident = next((active for active in active_residents if active.hostel_id == data['hostel'].id), None)
    moved_from = [active for active in active_residents if active is not resident]

    now = timezone.now()
    for stale in moved_from:
        stale.is_resident = False
        stale.end_date = now
        stale.save()
    message = f"Moved from {', '.join(stale.hostel.code for stale in moved_from)}" if moved_from else ''

    fields = _resident_fields(data, resident)
    if resident is None:
        Resident.objects.create(person=student.person, hostel=data['hostel'], start_date=now, **fields)
        return 'created', message

    changed = {name: value for name, value in fields.items() if getattr(resident, name) != value}
    for name, value in changed.items():
        setattr(resident, name, value)
    if changed:
        resident.save()
    return ('updated' if changed or moved_from else 'existing'), message


def _resident_fields(data, resident):
    fields = {
        'room_number': f"{data['room_no']}-{data['seat']}" if 'seat' in data else data['room_no'],
    }
    fields.update({field: data[key] for key, field in RESIDENT_FIELDS.items() if key in data})
    if 'admission_date' in data:
        fields['admission_date'] = timezone.make_aware(
            datetime.datetime.combine(data['admission_date'], datetime.time.min),
        )
    # A renamed parent gets a new person, as older residencies may share the current one.
    for key, relation in PARENT_FIELDS.items():
        parent = getattr(resident, relation, None)
        if key in data and (parent is None or parent.full_name != data[key]):
            fields[relation] = Person.objects.create(full_name=data[key])
    return fields


def _error_message(error):
    """
    Flattens a validation error into one line that names each field at fault
    """

    errors = getattr(error, 'detail', None) or getattr(error, 'message_dict', None)
    if not isinstance(errors, dict):
        return str(error)
    return '; '.join(f"{field}: {' '.join(messages)}" for field, messages in errors.items())
