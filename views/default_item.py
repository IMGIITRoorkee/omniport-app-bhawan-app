import swapper
import json
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bhawan_app.models import DefaultItem
from bhawan_app.serializers.default_item import DefaultItemSerializer
from bhawan_app.managers.services import is_hostel_admin, is_global_admin, is_warden, is_supervisor

Residence = swapper.load_model('kernel', 'Residence')

class DefaultItemViewset(viewsets.ModelViewSet):
    """
    Detail view for getting complaint item information of a single hostel
    """

    serializer_class = DefaultItemSerializer
    permission_classes = [IsAuthenticated,]
    allowed_methods = ['GET', 'POST', 'PATCH']

    def get_queryset(self):
        """
        Return the queryset of complaint items of a hostel
        :return: the queryset of complaint items of a hostel
        """

        hostel = self.kwargs['hostel__code']
        queryset = DefaultItem.objects.all()
        return queryset

    def create(self, request, hostel__code):
        """
        Create item instance if user has required permissions.
        :return: status code of the request
        """

        if not is_global_admin(request.person) and not is_hostel_admin(request.person, hostel__code) and not is_warden(request.person, hostel__code) and not is_supervisor(request.person, hostel__code):
            return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        name = data.get('name', None)

        instance = DefaultItem.objects.create(
            name = name,
            datetime_modified=datetime.now(),
        )
        return Response(DefaultItemSerializer(instance).data, status=status.HTTP_201_CREATED)

    