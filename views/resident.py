import swapper

from datetime import datetime

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
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


Person = swapper.load_model("Kernel", "Person")
Residence = swapper.load_model("kernel", "Residence")

class ResidentViewset(viewsets.ModelViewSet):
    """
    Detail view for getting information of a resident
    """

    serializer_class = ResidentSerializer
    allowed_methods = ['GET', 'POST', 'PATCH']
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if is_warden(request.person) or is_supervisor(request.person):
            pass
        else:
            raise PermissionDenied(
                "Only Supervisor and Warden are allowed to perform this action!",
            )

    def get_queryset(self):
        filters = self.get_filters(self.request)
        queryset = Resident.objects\
            .filter(**filters).order_by('-datetime_modified')
        return queryset

    def create(self, request, hostel__code):
        data = request.data
        try:
            person_id = data['person']
            room_number = data['room_number']
            person = Person.objects.get(id=person_id)
            hostel = Residence.objects.get(code=hostel__code)
            try:
                existing = Resident.objects.get(person=person)
                existing.delete()
            except Resident.DoesNotExist:
                pass
            instance = Resident.objects.create(
                person=person,
                room_number=room_number,
                hostel=hostel,
            )
            return Response(ResidentSerializer(instance).data)
        except Exception:
            return Response(
                "Bad request!",
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def retrieve(self, request, hostel__code, pk=None):
        enrolment_number = pk
        try:
            queryset = self.get_queryset()
            instance = queryset.get(person__student__enrolment_number=enrolment_number)
            return Response(ResidentSerializer(instance).data)
        except Exception:
            return Response(
                "Bad request!",
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, hostel__code, pk=None):
        try:
            enrolment_number = pk
            instance = Resident.objects.get(person__student__enrolment_number=enrolment_number)
            print(instance)
            instance.room_number = request.data['room_number']
            instance.save()
            return Response(ResidentSerializer(instance).data)
        except Exception:
            return Response(
                "Bad request!",
                status=status.HTTP_400_BAD_REQUEST,
            )

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