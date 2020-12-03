import swapper

from datetime import datetime
from distutils.util import strtobool

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ValidationError

from django.core.exceptions import ObjectDoesNotExist

from bhawan_app.models import Resident, HostelAdmin
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
        params = self.request.GET
        queryset = Resident.objects.all()
        queryset = self.apply_filters(self.request, queryset)
        return queryset

    def create(self, request, hostel__code):
        data = request.data
        try:
            person_id = data['person']
            room_number = data['room_number']
        except Exception:
            return Response(
                "Invalid field values for 'person' or 'room_number' !",
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            person = Person.objects.get(id=person_id)
        except Person.DoesNotExist:
            return Response(
                "Person doesn't exist !",
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            hostel = Residence.objects.get(code=hostel__code)
        except Residence.DoesNotExist:
            return Response(
                "Residence doesn't exist !",
                status=status.HTTP_404_NOT_FOUND,
            )
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
        
    
    def retrieve(self, request, hostel__code, pk=None):
        enrolment_number = pk
        try:
            queryset = self.get_queryset()
            instance = queryset.get(person__student__enrolment_number=enrolment_number)
            return Response(ResidentSerializer(instance).data)
        except Resident.DoesNotExist:
            return Response(
                "Resident does not exist !",
                status=status.HTTP_404_NOT_FOUND,
            )

    def partial_update(self, request, hostel__code, pk=None):
        data = request.data
        enrolment_number = pk
        try:
            instance = Resident.objects.get(person__student__enrolment_number=enrolment_number)
        except Resident.DoesNotExist:
            return Response(
                "Resident with this enrolment number doesn't exist !",
                status=status.HTTP_404_NOT_FOUND,
            )
        room_number = data.pop('room_number')
        if len(data) > 0:
            return Response(
                "You are only allowed to change room number of a person !",
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.save(room_number=room_number)
        return Response(ResidentSerializer(instance).data)

    def apply_filters(self, request, queryset):
        """
        Return a dict with all the filters populated with the
        filters received from query params.
        """
        filters = {}
        params = self.request.GET
        
        """
        Filter based on hostel
        """
        filters['hostel__code'] = self.kwargs['hostel__code']

        """
        Filter based on Year
        """
        year = params.get('year', None)
        if year:
            filters['person__student__current_year'] = year

        """
        Filter based on Branch
        """
        branch = params.get('branch', None)
        if branch:
            filters['person__student__branch__code'] = branch

        """
        Filter based on the fact, if person is admin
        """
        is_admin = params.get('is_admin', None)
        if is_admin:
            is_admin = strtobool(is_admin)
            hostel_admin_ids = HostelAdmin.objects.values_list('person__id', flat=True)
            if is_admin:
                queryset = queryset.filter(person__id__in=hostel_admin_ids)
            else:
                queryset = queryset.exclude(person__id__in=hostel_admin_ids)
        
        """
        Filter students
        """
        is_student = params.get('is_student', None)
        if is_student:
            is_student = strtobool(is_student)
            if is_student:
                queryset = queryset.filter(person__student__isnull=False)
            else:
                queryset = queryset.filter(person__student__isnull=True)
        
        queryset = queryset.filter(**filters).order_by('-datetime_modified')

        return queryset