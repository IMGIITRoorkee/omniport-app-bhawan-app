import pandas as pd

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import HttpResponse

from bhawan_app.managers.services import is_global_admin, is_hostel_admin, is_warden, is_supervisor
from bhawan_app.models import NonResidingStudent
from bhawan_app.models.roles.hostel_admin import HostelAdmin
from bhawan_app.serializers.non_residing_student import NonResidingStudentSerializer


class NonResidingStudentViewset(viewsets.ModelViewSet):
    """CRUD and download APIs for non-dining non-residing students."""

    serializer_class = NonResidingStudentSerializer
    permission_classes = [IsAuthenticated]
    allowed_methods = ['GET', 'POST', 'PATCH']
    pagination_class = None

    def _has_nrs_access_for_hostel(self, person, hostel_code):
        return (
            is_global_admin(person)
            or is_hostel_admin(person, hostel_code)
            or is_warden(person, hostel_code)
            or is_supervisor(person, hostel_code)
        )

    def get_queryset(self):
        hostel_code = self.kwargs['hostel__code']
        if not self._has_nrs_access_for_hostel(self.request.person, hostel_code):
            return NonResidingStudent.objects.none()
        return NonResidingStudent.objects.filter(hostel__code=hostel_code)

    def _is_any_hostel_admin(self, person):
        hostel_codes = HostelAdmin.objects.filter(person=person).values_list('hostel__code', flat=True)
        return any(is_hostel_admin(person, hostel_code) for hostel_code in hostel_codes if hostel_code)

    def _has_nrs_access_any_hostel(self, person):
        if is_global_admin(person):
            return True

        hostel_codes = HostelAdmin.objects.filter(person=person).values_list('hostel__code', flat=True)
        return any(
            (
                is_hostel_admin(person, hostel_code)
                or is_warden(person, hostel_code)
                or is_supervisor(person, hostel_code)
            )
            for hostel_code in hostel_codes
            if hostel_code
        )

    def all(self, request):
        if not self._has_nrs_access_any_hostel(request.person):
            return Response(
                {'detail': 'You are not allowed to perform this action!'},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = NonResidingStudent.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = {}
        hostel_code = self.kwargs.get('hostel__code')
        if hostel_code:
            context['hostel__code'] = hostel_code
        return context

    def create(self, request, hostel__code):
        if not self._has_nrs_access_for_hostel(request.person, hostel__code):
            return Response(
                {'detail': 'You are not allowed to perform this action!'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, hostel__code, pk=None):
        if not self._has_nrs_access_for_hostel(request.person, hostel__code):
            return Response(
                {'detail': 'You are not allowed to perform this action!'},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().partial_update(request, hostel__code, pk)

    @action(detail=False, methods=['get'])
    def download(self, request, hostel__code):
        if not self._has_nrs_access_for_hostel(request.person, hostel__code):
            return Response(
                {'detail': 'You are not allowed to perform this action!'},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = self.get_queryset()
        data = {
            'Name of the bhawan': [],
            'Name': [],
            'Designation': [],
            'Department': [],
            'Mobile number': [],
            'Room number': [],
            'From (date)': [],
            'Upto (date)': [],
            'Email-id': [],
        }

        for student in queryset:
            data['Name of the bhawan'].append(student.hostel.name)
            data['Name'].append(student.name)
            data['Designation'].append(student.get_designation_display())
            data['Department'].append(student.department)
            data['Mobile number'].append(student.mobile_number)
            data['Room number'].append(student.room_number)
            data['From (date)'].append(student.from_date)
            data['Upto (date)'].append(student.upto_date)
            data['Email-id'].append(student.email_id)

        file_name = f'{hostel__code}_non_residing_students.csv'
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        df.to_csv(path_or_buf=response, index=False)
        return response
