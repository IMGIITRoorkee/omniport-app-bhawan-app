from datetime import datetime

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from bhawan_app.models import Complaint, Resident
from bhawan_app.serializers.complaint import ComplaintSerializer
from bhawan_app.managers.services import (
    is_warden, 
    is_supervisor, 
    is_hostel_admin
)
from bhawan_app.constants import statuses   
from bhawan_app.constants import complaint_types
from bhawan_app.pagination.custom_pagination import CustomPagination 


class ComplaintViewset(viewsets.ModelViewSet):
    """
    Detail view for getting complaint information of a single hostel
    """

    serializer_class = ComplaintSerializer
    allowed_methods = ['GET', 'POST', 'PATCH']
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @action(detail=True, methods=['GET'])
    def unsuccessful(self, request, hostel__code, pk=None):
        instance = self.get_object()
        if instance.status == statuses.UNRESOLVED:
            return Response(
                {"error": "Action forbidden !"},
                status.HTTP_403_FORBIDDEN,
            )

        if is_warden(request.person) or is_supervisor(request.person):
            count = instance.failed_attempts
            updates = {}
            if count < 3:
                instance.failed_attempts += 1
            if count == 3:
                instance.status = statuses.UNRESOLVED
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        return Response(
            {"error": "You are not allowed to perform this action !"},
            status.HTTP_403_FORBIDDEN,
        )

    def get_queryset(self):
        filters = self.get_filters(self.request)
        queryset = Complaint.objects\
            .filter(**filters).order_by('-datetime_modified')
        return queryset

    def get_serializer_context(self):
        return {
            "person": self.request.person,
        }

    def create(self, request, hostel__code):
        person = request.person
        description = request.data['description']
        complaint_type = request.data['complaint_type']
        try:
            resident = Resident.objects.get(person=person)
        except Resident.DoesNotExist:
            return Response(
                "Resident doesn't exist !"
            )
        instance = Complaint.objects.create(
            resident=resident,
            status=statuses.PENDING,
            datetime_modified=datetime.now(),
            description=description,
            complaint_type=complaint_type,
        )
        return Response(ComplaintSerializer(instance).data)

    def retrieve(self, request, hostel__code, pk=None):
        queryset = self.get_queryset()
        try:
            complaint = queryset.get(pk=pk)
        except ObjectDoesNotExist:
            complaint = Complaint.objects.none()
        serializer = ComplaintSerializer(complaint)
        return Response(serializer.data)
    
    def partial_update(self, request, hostel__code, pk=None):
        instance = get_object_or_404(Complaint, pk=pk)
        if not is_warden(request.person) and \
                not is_supervisor(request.person):
            return Response(
                "Only Supervisor and Warden are allowed to perform this action!",
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ComplaintSerializer(instance, data=request.data, partial=True)
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
        Apply the filters for statuses.
        Usage: /complaint/?status=<status_in_uppercase>
        """
        if 'status' in params.keys():
            status_list = params.getlist('status')
            mapping = statuses.COMLAINT_STATUSES_MAP
            status_codes = [\
                mapping[key] for key in status_list\
                if key in mapping.keys()\
            ]
            filters['status__in'] = status_codes

        """
        Apply the filters for types.
        Usage: /complaint/?type=<type_in_uppercase>
        """
        if 'type' in params.keys():
            complaint_type = params['type']
            if complaint_type in complaint_types.COMPLAINT_TYPES_MAP.keys():
                filters['complaint_type'] = \
                    complaint_types.COMPLAINT_TYPES_MAP[complaint_type]
        
        """
        Filter based on hostel
        """
        filters['resident__hostel__code']= self.kwargs["hostel__code"]

        """
        If not hostel admin, list the booking by the person only. Person is the 
        currently authenticated user.
        """
        if not is_hostel_admin(request.person):
            print("*"*50)
            print(request.user.person)
            print("*"*50)
            filters['resident__person'] = request.person.id
        return filters