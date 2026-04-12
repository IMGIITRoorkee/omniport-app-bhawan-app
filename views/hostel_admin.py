import swapper
from distutils.util import strtobool

from django.db import IntegrityError
from django.db.models import Case, When, Value, IntegerField

from rest_framework import viewsets, status
from rest_framework.response import Response

from bhawan_app.models.roles.hostel_admin import HostelAdmin
from bhawan_app.models.resident import Resident
from bhawan_app.serializers.hostel_admin import HostelAdminSerializer
from bhawan_app.constants import designations
from bhawan_app.managers.services import is_warden, is_global_admin, is_supervisor
    
Person = swapper.load_model('Kernel', 'Person')
Hostel = swapper.load_model('Kernel', 'Residence')

class HostelAdminViewset(viewsets.ModelViewSet):
    """
    CRUD views for getting admin information of all hostels
    """

    serializer_class = HostelAdminSerializer
    allowed_methods = ['GET', 'POST', 'PATCH',]
    pagination_class = None

    def get_queryset(self):
        """
        Return the queryset of profile grouped by a hostel
        :return: the queryset of profile grouped by a hostel
        """
        filters = self.get_filters(self.request)
        ordered_designations = [
            designations.CHIEF_WARDEN,
            designations.MESS_WARDEN,
            designations.WARDEN_WELLNESS,
            designations.ASSISTANT_WARDEN,
            designations.ASSISTANT_WARDEN_2,
            designations.BHAWAN_SECRETARY,
            designations.TECHNICAL_SECRETARY,
            designations.SUPERVISOR,
            designations.ASSISTANT_WARDEN_3,
            designations.MESS_SECRETARY,
            designations.MAINTENANCE_SECRETARY,
            designations.SPORTS_SECRETARY,
            designations.CULTURAL_SECRETARY,
            designations.WELLNESS_SECRETARY,
        ]
        queryset = HostelAdmin.objects.filter(**filters).annotate(
            designation_rank=Case(
                *[
                    When(designation=designation, then=Value(index))
                    for index, designation in enumerate(ordered_designations)
                ],
                default=Value(999),
                output_field=IntegerField(),
            )
        ).order_by('designation_rank', 'id')
        return queryset

    def get_filters(self, request):
        """
        Return a dict with all the filters populated with the
        filters received from query params.
        """
        filters = {}
        params = self.request.GET

        """
        Apply the filters for statuses.
        Usage: /admin/?student=true gives all hostel admins which are
        students.
        """

        student = params.get('student', None)
        if student:
            student = strtobool(student)
            if student:
                filters['designation__in'] = designations.STUDENT_COUNCIL_LIST

        """
        Filter based on hostel
        """
        filters['hostel__code']= self.kwargs['hostel__code']
        return filters

    def create(self, request, hostel__code, pk=None):
        if is_warden(request.person, hostel__code) or is_global_admin(request.person) or is_supervisor(request.person, hostel__code):
            try:
                data = request.data
                serializer = self.get_serializer(data=data)
                designation = request.data['designation']
                serializer.is_valid(raise_exception=True)
                person = Person.objects.get(pk=data['person'])
                hostel = Hostel.objects.get(code=hostel__code)
                residents = Resident.objects.filter(person=person, hostel = hostel, is_resident = True)
                is_resident = residents.exists()


                if designation in designations.GLOBAL_COUNCIL_LIST and not is_global_admin(request.person):
                    return Response(
                        "You are not allowed to create a global admin",
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if designation in designations.STUDENT_COUNCIL_LIST and not is_resident:
                    return Response(
                        f"{person.full_name} is not a registered resident",
                        status=status.HTTP_403_FORBIDDEN,
                    )

                serializer.save(
                    person=person,
                    hostel=hostel,
                )

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )

            except IntegrityError:
                return Response(
                    "One person can hold only one office and one office can be held by one person",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            except Exception as error:
                return Response(
                    str(error),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            'Only warden is allowed to perform this action !',
            status=status.HTTP_403_FORBIDDEN,
        )

    def partial_update(self, request, hostel__code, pk=None):
        if is_warden(request.person, hostel__code) or is_global_admin(request.person) or is_supervisor(request.person, hostel__code):
            try:
                instance = self.get_object()
                serializer = self.get_serializer(
                    instance,
                    data=request.data,
                    partial=True,
                )
                serializer.is_valid(raise_exception=True)
                if 'person' in request.data.keys():
                    person = Person.objects.get(pk=request.data['person'])
                    serializer.save(person=person)
                else:
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            except IntegrityError:
                return Response(
                    "One person can hold only one office and one office can be held by one person",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            except Exception as error:
                return Response(
                    str(error),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            'Only warden is allowed to perform this action !',
            status=status.HTTP_403_FORBIDDEN,
        )
