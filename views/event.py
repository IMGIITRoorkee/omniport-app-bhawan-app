from datetime import datetime

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status

from bhawan_app.models import Event
from bhawan_app.serializers.event import EventSerializer
from bhawan_app.pagination.custom_pagination import CustomPagination
from bhawan_app.managers.services import is_hostel_admin


class EventViewset(viewsets.ModelViewSet):
    """
    Detail view for getting event information of a single hostel
    """

    serializer_class = EventSerializer
    pagination_class = CustomPagination
    allowed_methods = ['GET', 'POST', 'PATCH',]

    def get_queryset(self):
        """
        Return the queryset of events of a hostel
        :return: the queryset of events of a hostel
        """

        hostel_code = self.kwargs["hostel__code"]
        queryset = Event.objects.filter(hostel__code=hostel_code)

        return queryset

    def get_serializer_context(self):
        return {
            'hostel__code': self.kwargs['hostel__code'],
        }

    def partial_update(self, request, hostel__code, pk=None):
        """
        Update the event instance iff the logged in user is Admin
        :return: Updated instance
        """
        if is_global_admin(req.person) or is_hostel_admin(request.person, hostel__code):
            return super().partial_update(request, hostel__code, pk)
        return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
        )

