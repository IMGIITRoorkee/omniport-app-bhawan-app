import swapper
import pandas as pd

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from bhawan_app.models import StudentAccommodation, Room
from bhawan_app.serializers.student_accommodation import StudentAccommodationSerializer
from bhawan_app.managers.services import is_hostel_admin, is_global_admin
from bhawan_app.constants import room_types,room_occupancy

Residence = swapper.load_model('kernel', 'Residence')


class StudentAccommodationViewset(viewsets.ModelViewSet):
    """
    Detail view for getting information about students residing and needing accomodation in a single hostel
    """

    serializer_class = StudentAccommodationSerializer
    permission_classes = [IsAuthenticated,]
    allowed_methods = ['GET', 'POST', 'PATCH']
    pagination_class = None

    def get_queryset(self):
        """
        Return the queryset of students residing and needing accommodation in a hostel
        :return: the queryset of students residing and needing accommodation in a hostel
        """

        hostel = self.kwargs['hostel__code']
        queryset = StudentAccommodation.objects.filter(hostel__code=hostel)

        return queryset

    def get_serializer_context(self):
        return {
            'hostel__code': self.kwargs['hostel__code'],
        }

    def create(self, request, hostel__code):
        """
        Create Student Accommodation instance if user has required permissions.
        :return: status code of the request
        """
        if not is_global_admin(request.person) and not is_hostel_admin(request.person, hostel__code):
            return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
            )
        try:
            hostel = Residence.objects.get(code=hostel__code)
            data = {}
            for field in self.request.POST:
                data[field] = "".join(self.request.POST[field])
            student_accommodation = StudentAccommodation.objects.create(
                hostel = hostel,
                **data,
            )

            return Response(StudentAccommodationSerializer(student_accommodation).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, hostel__code, pk=None):
        """
        Update Student Accommodation instance if user has required permissions.
        :return: updated Student Accommodation instance
        """
        if is_hostel_admin(request.person, hostel__code) or is_global_admin(request.person):
            return super().partial_update(request, hostel__code, pk)

        return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
        )

    
    @action(detail=False, methods=['get'])
    def download_all(self, request):
        """
        This method exports a csv with details of accomodation
        in each hostel.
        """
        
        if not is_global_admin(request.person):
            return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
            )

        queryset = Residence.objects.all()
        data = {
            'Bhawan': [],
            'Net accommodation capacity': [],
            'Presently residing registered residents': [],
            'Presently residing non-registered residents': [],
            'Total residents': [],
            'Present vacant seats for students':[],
        }
        for residence in queryset:
            data['Bhawan'].append(residence.name)
            total_residents = 0

            try:
                registered_accommodation =  StudentAccommodation.objects.get(hostel = residence , is_registered = True)
                total_registered_residents = registered_accommodation.residing_in_single + registered_accommodation.residing_in_double \
                                            + registered_accommodation.residing_in_triple
                total_residents = total_residents + total_registered_residents
                data['Presently residing registered residents'].append(total_registered_residents)
            except:
                data['Presently residing registered residents'].append(0)

            try:
                non_registered_accommodation =  StudentAccommodation.objects.get(hostel = residence , is_registered = False)
                total_non_registered_residents = non_registered_accommodation.residing_in_single + non_registered_accommodation.residing_in_double \
                                            + non_registered_accommodation.residing_in_triple
                total_residents = total_residents + total_non_registered_residents                            
                data['Presently residing non-registered residents'].append(total_non_registered_residents)
            except:
                data['Presently residing non-registered residents'].append(0)

            data['Total residents'].append(total_residents)
            rooms = Room.objects.filter(hostel = residence)
            accommodation_capacity = 0

            for room in rooms:
                capacity = room.count
                if(room.occupancy == room_occupancy.DOUBLE):
                    capacity = capacity*2
                if(room.occupancy == room_occupancy.TRIPLE):
                    capacity = capacity*3
                if room.room_type == room_types.TOTAL:
                    accommodation_capacity = accommodation_capacity + capacity
                else:
                    accommodation_capacity = accommodation_capacity - capacity

            data['Net accommodation capacity'].append(accommodation_capacity)
            data['Present vacant seats for students'].append(accommodation_capacity-total_residents)
        file_name = 'Bhawan_accommodation_list.csv'
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        df.to_csv(path_or_buf=response, index=False)
        return response
