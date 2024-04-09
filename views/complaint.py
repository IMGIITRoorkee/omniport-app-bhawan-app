import datetime
import pandas as pd

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from bhawan_app.models import Complaint, Resident
from bhawan_app.models.roles import HostelAdmin
from bhawan_app.views.utils import get_phone_number
from bhawan_app.serializers.complaint import ComplaintSerializer
from bhawan_app.managers.services import (
    is_warden,
    is_supervisor,
    is_hostel_admin,
    is_global_admin,
)
from bhawan_app.constants import statuses
from bhawan_app.constants import complaint_types 
from bhawan_app.utils.notification.push_notification import send_push_notification
from bhawan_app.utils.email.send_email import send_email


class ComplaintViewset(viewsets.ModelViewSet):
    """
    Detail view for getting complaint information of a single hostel
    """

    serializer_class = ComplaintSerializer
    allowed_methods = ['GET', 'POST', 'PATCH']
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @action(detail=True, methods=['GET'])
    def unsuccessful(self, request, hostel__code, pk=None):
        instance = self.get_object()
        if instance.status == statuses.UNRESOLVED:
            return Response(
                {"error": "Action forbidden !"},
                status.HTTP_403_FORBIDDEN,
            )

        if is_warden(request.person, hostel__code) or is_supervisor(request.person, hostel__code) or is_global_admin(request.person):
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
        queryset = self.apply_filters(self.request)
        return queryset

    def get_serializer_context(self):
        return {
            "person": self.request.person,
        }

    def create(self, request, hostel__code):
        person = request.person
        data = request.data
        description = data.get('description', None)
        complaint_type = data.get('complaint_type', None)
        if not description:
            return Response(
                "Description can't be left empty !",
                status.HTTP_404_NOT_FOUND,
            )
        if not complaint_type:
            return Response(
                "Complaint type can't be left empty !",
                status.HTTP_404_NOT_FOUND,
            )
        try:
            resident = Resident.objects.get(person=person, is_resident = True)
        except Resident.DoesNotExist:
            return Response(
                "Resident doesn't exist !",
                status.HTTP_404_NOT_FOUND,
            )
        instance = Complaint.objects.create(
            resident=resident,
            status=statuses.PENDING,
            datetime_modified=datetime.datetime.now(),
            description=description,
            complaint_type=complaint_type,
        )
        template = f"New Complaint regarding {instance.complaint_type} by {instance.resident} "
        email_subject = f"{instance.resident} complained '{instance.description}' regarding {instance.complaint_type}"
        email_body = f""
        hostel = instance.resident.hostel.id
        all_staff = HostelAdmin.objects.filter(hostel=hostel)
        notify_users = [staff.person.id for staff in all_staff]
        send_push_notification(template, True, persons=notify_users,send_only_to_subscribed_users=True)
        send_email(email_subject, email_body, notify_users, True, person.id,send_only_to_subscribed_users=True,)

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
        if not is_warden(request.person, hostel__code) and \
                not is_supervisor(request.person, hostel__code) and \
                    not is_global_admin(request.person):
            return Response(
                "Only Supervisor and Warden are allowed to perform this action!",
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ComplaintSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(datetime_modified=datetime.datetime.now())
        return Response(serializer.data)

    def apply_filters(self, request):
        """
        Return a dict with all the filters populated with the
        filters received from query params.
        """
        filters = {}
        search_query = Q()
        date_query = Q()
        params = self.request.GET
        
        """
        Apply the filters for statuses.
        Usage: /complaint/?status=<status_in_uppercase>
        """
        if 'status' in params.keys():
            status_list = params.getlist('status')
            mapping = statuses.COMPLAINT_STATUSES_MAP
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
        Apply the filters based on search(Name/Enrollment no.).
        Usage: /complaint/?search=<searchkeyword_in_uppercase>
        """
        if 'search' in params.keys():
            search = params['search']
            if len(search):
                search_query = Q(resident__person__student__enrolment_number__contains=search) | Q(resident__person__full_name__icontains=search)

        """
        Apply the filters based on start date and end date.
        Usage: /complaint/?date=<start_date>/<end_date>
        """
        if 'date' in params.keys():
            data = params['date'].split('/')
            start_date, end_date = data[0], data[1]
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.combine(end_date, datetime.time.max)
            if start_date and end_date:
                date_query = Q(datetime_created__range=(start_date, end_date))

        """
        Filter based on hostel
        """
        filters['resident__hostel__code']= self.kwargs["hostel__code"]

        me = params.get('me')

        """
        If not hostel admin, list the booking by the person only. Person is the
        currently authenticated user.
        """
        if me or (not is_hostel_admin(request.person, self.kwargs["hostel__code"]) and not is_global_admin(request.person)):
            filters['resident__person'] = request.person.id

        queryset = Complaint.objects.filter(**filters).filter(search_query).filter(date_query).order_by('-datetime_modified')
     
        return queryset

    @action(detail=False, methods=['get'])
    def download(self, request, hostel__code):
        """
        This method exports a csv corresponding to the list
        of complaints
        """
        params = self.request.GET
        queryset = self.apply_filters(self.request)
        data = {
            'Applicant Name': [],
            'Complaint Date': [],
            'Complaint Type': [],
            'Description': [],
            'Contact No.': [],
            'Applicant Room': [],
            'Unsuccesful attempts': [],
            'Status': [],
        }
        for complaint in queryset:
            try:
                data['Applicant Name'].append(complaint.resident.person.full_name)
                data['Complaint Date'].append(complaint.datetime_created.strftime("%I:%M%p %d%b%Y"))
                data['Complaint Type'].append(complaint.get_complaint_type_display())
                data['Description'].append(complaint.description)
                data['Contact No.'].append(get_phone_number(complaint.resident))
                data['Applicant Room'].append(complaint.resident.room_number)
                data['Unsuccesful attempts'].append(complaint.failed_attempts)
                data['Status'].append(complaint.get_status_display())
            except IndexError:
                pass

        file_name = f'{hostel__code}_complaints_list.csv'
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        df.to_csv(path_or_buf=response, index=False)
        return response
