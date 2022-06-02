import swapper
import json

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bhawan_app.models import Room
from bhawan_app.models.roles import HostelAdmin
from bhawan_app.serializers.room import RoomSerializer
from bhawan_app.managers.services import is_hostel_admin, is_global_admin
from bhawan_app.constants import room_types, room_occupancy
# from bhawan_app.utils.notification.push_notification import send_push_notification

Residence = swapper.load_model('kernel', 'Residence')


class RoomViewset(viewsets.ModelViewSet):
    """
    Detail view for getting rooms information of a single hostel
    """

    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated,]
    allowed_methods = ['GET', 'POST', 'PATCH']
    pagination_class = None

    def get_queryset(self):
        """
        Return the queryset of rooms of a hostel
        :return: the queryset of rooms of a hostel
        """

        hostel = self.kwargs['hostel__code']
        queryset = Room.objects.filter(hostel__code=hostel)

        return queryset

    def get_serializer_context(self):
        return {
            'hostel__code': self.kwargs['hostel__code'],
        }

    def create(self, request, hostel__code):
        """
        Create room instance if user has required permissions.
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
            room = Room.objects.create(
                hostel = hostel,
                **data,
            )

            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, hostel__code, pk=None):
        """
        Update room instance if user has required permissions.
        :return: updated room instance
        """
        if is_hostel_admin(request.person, hostel__code) or is_global_admin(request.person):
            return super().partial_update(request, hostel__code, pk)

        return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def delete(self, request, hostel__code, pk):
        """
        Delete room instance if user has required permissions.
        """
        if not is_hostel_admin(request.person, hostel__code) and not is_global_admin(req.person):
            return Response(
                {"You are not allowed to perform this action !"},
                status=status.HTTP_403_FORBIDDEN,
            )

        hostel = Residence.objects.get(code=hostel__code)
        room = Room.objects.get(pk=pk)
        room.hostel.remove(hostel)
        # If there is no hostel remaining attached to this room remove it
        if not room.hostel.exists():
            room.delete()
        return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_200_OK,
        )