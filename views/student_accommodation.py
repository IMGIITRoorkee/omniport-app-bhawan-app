import swapper
import json

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bhawan_app.models import StudentAccommodation
from bhawan_app.models.roles import HostelAdmin
from bhawan_app.serializers.student_accommodation import StudentAccommodationSerializer
from bhawan_app.managers.services import is_hostel_admin, is_global_admin


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