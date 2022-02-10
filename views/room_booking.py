import json
import swapper
import pandas as pd
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bhawan_app.models import RoomBooking, Visitor, Resident
from bhawan_app.views.utils import get_phone_number
from bhawan_app.serializers.room_booking import RoomBookingSerializer
from bhawan_app.managers.services import is_hostel_admin, is_supervisor, is_warden, is_global_admin
from bhawan_app.constants import statuses
from bhawan_app.pagination.custom_pagination import CustomPagination

Person = swapper.load_model('kernel', 'Person')


class RoomBookingViewset(viewsets.ModelViewSet):

    """
    Detail view for getting contact information of a single hostel
    """

    serializer_class = RoomBookingSerializer
    allowed_methods = ['GET', 'PATCH', 'POST']
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


    def get_queryset(self):
        """
        Return the queryset of bookings grouped by a hostel
        :return: the queryset of bookings grouped by a hostel
        """

        filters = self.get_filters(self.request)
        queryset = RoomBooking.objects\
            .filter(**filters).order_by('-datetime_modified')
        return queryset

    def create(self, request, hostel__code):
        file_data = self.request.FILES
        visitors = self.request.POST.pop('visitors')
        try:
            resident = Resident.objects.get(person=request.person, is_resident = True)
        except Resident.DoesNotExist:
            return Response(
                f'{request.person} is not a registered resident',
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            sanitized_data = {}
            for data in self.request.POST:
                sanitized_data[data] = self.request.POST[data]

            room_booking = RoomBooking.objects.create(
                resident=resident,
                **sanitized_data,
            )
            visitor_index = 0
            for visitor in visitors:
                visitor = json.loads(visitor)
                visitor_full_name = visitor.pop('full_name')
                visitor_person = Person.objects.create(
                    full_name=visitor_full_name,
                )
                file_name = f'visitors_{visitor_index}'
                photo_identification = file_data.get(file_name)
                Visitor.objects.create(
                    person=visitor_person,
                    photo_identification=photo_identification,
                    booking=room_booking, **visitor,
                )
                visitor_index += 1
            return Response(
                'Room booking requested',
                status=status.HTTP_201_CREATED,
            )
        except Exception as error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, hostel__code, pk=None):
        data = request.data
        instance = get_object_or_404(RoomBooking, pk=pk)
        if 'status' in data.keys():
            if data['status'] == statuses.FORWARDED:
                if not is_supervisor(request.person, hostel__code) and not is_global_admin(request.person):
                    return Response(
                        "Only Supervisor is allowed to perform this action!",
                        status=status.HTTP_403_FORBIDDEN,
                    )
            elif not is_warden(request.person, hostel__code) and not is_global_admin(request.person):
                return Response(
                    "Only Warden is allowed to perform this action!",
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not self.is_valid(data['status'], instance.status):
                return Response(
                    "Invalid action!",
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = RoomBookingSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(datetime_modified=datetime.now())
        return Response(serializer.data)

    def is_valid(self, new_status, prev_status):
        """
        Checks to ensure the proper flow of statuses:
        1. Only forwarded request can be approved.
        2. Only pending request can be forwarded.
        3. Status of a rejected request can't be changed.
        """

        if prev_status == statuses.REJECTED:
            return False
        if new_status == statuses.FORWARDED:
            return prev_status == statuses.PENDING
        if new_status == statuses.APPROVED:
            return prev_status == statuses.FORWARDED
        if new_status == statuses.CONFIRMED:
            return prev_status == statuses.APPROVED
        return True

    def get_filters(self, request):
        """
        Return a dict with all the filters populated with the
        filters received from query params.
        """
        filters = {}
        params = self.request.GET

        """
        Apply the filters for statuses.
        Usage: /complaint/?status=<status_in_uppercase>
        """
        if 'status' in params.keys():
            status = params['status']
            if status in statuses.BOOKING_STATUSES_MAP.keys():
                filters['status'] = statuses.BOOKING_STATUSES_MAP[status]

        """
        Filter based on hostel
        """
        filters['resident__hostel__code'] = self.kwargs["hostel__code"]

        """
        Filter based on date of booking, if past=True then filter booking which
        are reqeusted from a date date that has passed
        """
        # if 'past' in params.keys():
        #     if params['past'] == 'true':
        #         filters['requested_from__lt'] = datetime.now()
        #     elif params['past'] == 'false':
        #         filters['requested_from__gte'] = datetime.now()

        """
        If not hostel admin, list the booking by the person only.
        """
        if not is_hostel_admin(request.person, self.kwargs["hostel__code"]):
            filters['resident__person'] = request.person.id
        return filters

    @action(detail=False, methods=['get'])
    def download(self, request, hostel__code):
        """
        This method exports a csv corresponding to the list
        of room bookings
        """
        params = self.request.GET
        filters = self.get_filters(self.request)
        queryset = RoomBooking.objects\
            .filter(**filters).order_by('-datetime_modified')
        data = {
            'Applicant Name': [],
            'Start Date': [],
            'End Date': [],
            'Contact No.': [],
            'Applicant Room': [],
            'Visitors': [],
            'Status': [],
        }
        for booking in queryset:
            try:
                data['Applicant Name'].append(booking.resident.person.full_name)
                data['Start Date'].append(booking.requested_from.strftime("%I:%M%p %d%b%Y"))
                data['End Date'].append(booking.requested_till.strftime("%I:%M%p %d%b%Y"))
                data['Contact No.'].append(get_phone_number(booking.resident))
                data['Applicant Room'].append(booking.resident.room_number)
                data['Visitors'].append(Visitor.objects.filter(booking=booking).count())
                data['Status'].append(booking.status)
            except IndexError:
                pass

        file_name = f'{hostel__code}_bookings_list.csv'
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        df.to_csv(path_or_buf=response, index=False)
        return response