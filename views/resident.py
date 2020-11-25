from datetime import datetime

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from django.core.exceptions import ObjectDoesNotExist

from bhawan_app.models import Resident
from bhawan_app.serializers.resident import ResidentSerializer
from bhawan_app.managers.services import (
    is_warden, 
    is_supervisor, 
    is_hostel_admin
)
from bhawan_app.pagination.custom_pagination import CustomPagination 


class ResidentViewset(viewsets.ModelViewSet):
    """
    Detail view for getting complaint information of a single hostel
    """

    serializer_class = ResidentSerializer
    allowed_methods = ['GET', 'POST', 'PATCH']
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def initial(self, request, *args, **kwargs):
        return super().initial(request, *args, **kwargs)
        if not is_warden(request.person) and \
                not is_supervisor(request.person):
            return Response(
                "Only Supervisor and Warden are allowed to perform this action!",
                status=status.HTTP_403_FORBIDDEN,
            )

    def get_queryset(self):
        filters = self.get_filters(self.request)
        queryset = Resident.objects\
            .filter(**filters).order_by('-datetime_modified')
        return queryset

    def partial_update(self, request, hostel__code, pk=None):
        instance = self.get_object()
        serializer = ResidentSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(datetime_modified=datetime.now())
        return Response(serializer.data)

    def get_filters(self, request):
        """
        Return a dict with all the filters populated with the
        filters received from query params.
        """
        filters = {}
        params = self.request.GET
        
        """
        Filter based on hostel
        """
        filters['hostel__code'] = self.kwargs["hostel__code"]

        return filters