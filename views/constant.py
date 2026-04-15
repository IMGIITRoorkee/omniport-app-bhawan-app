import swapper

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from bhawan_app.constants import (
    designations,
    complaint_types,
    complaint_items,
    statuses,
    days,
    room_types,
    room_occupancy
)

Hostel = swapper.load_model('Kernel', 'Residence')
Branch = swapper.load_model('Kernel', 'Branch')
Degree = swapper.load_model('Kernel', 'Degree')


class ConstantViewset(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    List view for constants and their codes
    """
    renderer_classes = [JSONRenderer,]

    def list(self, request):
        """
        Return JSONified dictionary of constants and corresponding codes.
        :return: dictionay of contants and codes
        """
        mapping = designations.STUDENT_COUNCIL_MAP
        reverse_student_council_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = designations.ADMINISTRATIVE_COUNCIL_MAP
        reverse_administrative_council_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = designations.GLOBAL_COUNCIL_MAP
        reverse_global_council_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = complaint_types.COMPLAINT_TYPES_MAP
        reverse_complaint_types_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = complaint_items.COMPLAINT_ITEMS_MAP
        reverse_complaint_items_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = statuses.COMPLAINT_STATUSES_MAP
        reverse_complaint_statuses_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = statuses.BOOKING_STATUSES_MAP
        reverse_booking_statuses_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = statuses.FEE_TYPES_MAP
        reverse_fee_types_map = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = days.DAYS_MAP
        reverse_days = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = room_types.ROOM_TYPES_MAP
        reverse_room_types = \
            {mapping[key]: key for key in mapping.keys()}
        mapping = room_occupancy.ROOM_OCCUPANCY_MAP
        reverse_room_occupancy = \
            {mapping[key]: key for key in mapping.keys()}

        response = {}
        reverse_designations_map = {
            **reverse_student_council_map,
            **reverse_administrative_council_map,
            **reverse_global_council_map,
        }
        ordered_designation_codes = [
            designations.CHIEF_WARDEN,
            designations.MESS_WARDEN,
            designations.WARDEN_WELLNESS,
            designations.ASSISTANT_WARDEN,
            designations.ASSISTANT_WARDEN_2,
            designations.BHAWAN_SECRETARY,
            designations.TECHNICAL_SECRETARY,
            designations.SUPERVISOR,
            designations.ASSISTANT_WARDEN_3,
            designations.MESS_SECRETARY,
            designations.MAINTENANCE_SECRETARY,
            designations.SPORTS_SECRETARY,
            designations.CULTURAL_SECRETARY,
            designations.WELLNESS_SECRETARY,
        ]
        response['designations'] = {
            code: reverse_designations_map[code]
            for code in ordered_designation_codes
            if code in reverse_designations_map
        }
        response['designations'].update(
            {
                code: label
                for code, label in reverse_designations_map.items()
                if code not in response['designations']
            }
        )
        response['global_council'] = designations.GLOBAL_COUNCIL_LIST
        response['student_council'] = designations.STUDENT_COUNCIL_LIST
        response['administrative_council'] = designations.ADMINISTRATIVE_COUNCIL_LIST
        response['complaint_types'] = reverse_complaint_types_map
        response['complaint_items'] = reverse_complaint_items_map
        response['statuses'] = {
            'COMPLAINT_STATUSES': reverse_complaint_statuses_map,
            'BOOKING_STATUSES': reverse_booking_statuses_map,
            'FEE_TYPES': reverse_fee_types_map,
        }
        response['days'] = reverse_days
        response['room_types'] = reverse_room_types
        response['room_types_list'] = room_types.ROOM_TYPES_LIST
        response['room_occupancy'] = reverse_room_occupancy
        response['room_occupancy_list'] = room_occupancy.ROOM_OCCUPANCY_LIST

        hostels = Hostel.objects.all()
        response['hostels'] = {
            hostel.code: hostel.name for hostel in hostels
        }
        branches = Branch.objects.values('name', 'code')
        response['branches'] = {
            branch['code']: branch['name'] for branch in branches
        }
        branches = Branch.objects.all()
        response['departments'] = {
            branch.department.code: branch.department.name for branch in branches
        }
        response['degrees'] = Degree.objects.values_list('code', flat = True)
        return Response(response)
