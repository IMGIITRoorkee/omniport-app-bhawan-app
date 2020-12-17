import swapper
import json

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bhawan_app.models import Facility
from bhawan_app.models import Timing
from bhawan_app.serializers.facility import FacilitySerializer
from bhawan_app.managers.services import is_hostel_admin

Residence = swapper.load_model('kernel', 'Residence')


class FacilityViewset(viewsets.ModelViewSet):
    """
    Detail view for getting facility information of a single hostel
    """

    serializer_class = FacilitySerializer
    permission_classes = [IsAuthenticated,]
    allowed_methods = ['GET', 'POST', 'PATCH']
    pagination_class = None

    def get_queryset(self):
        """
        Return the queryset of facilities of a hostel
        :return: the queryset of facilities of a hostel
        """

        hostel = self.kwargs['hostel__code']
        queryset = Facility.objects.filter(hostel__code=hostel)

        return queryset

    def get_serializer_context(self):
        return {
            'hostel__code': self.kwargs['hostel__code'],
        }

    def create(self, request, hostel__code):
        """
        Create facility instance if user has required permissions.
        :return: status code of the request
        """

        if not is_hostel_admin(request.person):
            return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
            )
        try:
            hostel = Residence.objects.get(code=hostel__code)
            timings = self.request.POST.pop('timings')
            display_picture = self.request.FILES.get('display_picture')

            data = {}
            for field in self.request.POST:
                data[field] = "".join(self.request.POST[field])
            facility = Facility.objects.create(
                display_picture=display_picture,
                **data,
            )
            facility.hostel.add(hostel)
            for timing in timings:
                timing = json.loads(timing)
                timing_object = Timing.objects.create(**timing)
                facility.timings.add(timing_object)

            return Response('Facility created', status=status.HTTP_201_CREATED)
        except Exception:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, hostel__code, pk=None):
        """
        Update facility instance if user has required permissions.
        :return: updated facility instance
        """
        if is_hostel_admin(request.person):
            return super().partial_update(request, hostel__code, pk)

        return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def delete(self, request, hostel__code, pk):
        """
        Delete facility instance if user has required permissions.
        """
        if not is_hostel_admin(request.person):
            return Response(
                {"You are not allowed to perform this action !"},
                status=status.HTTP_403_FORBIDDEN,
            )

        hostel = Residence.objects.get(code=hostel__code)
        facility = Facility.objects.get(pk=pk)
        facility.hostel.remove(hostel)
        # If there is no hostel remaining attached to this facility remove it
        if not facility.hostel.exists():
            facility.delete()
        return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_200_OK,
        )