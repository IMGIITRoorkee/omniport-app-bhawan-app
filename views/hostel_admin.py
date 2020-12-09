import swapper
from datetime import date
from distutils.util import strtobool

from rest_framework import viewsets, status
from rest_framework.response import Response

from bhawan_app.models.roles.hostel_admin import HostelAdmin
from bhawan_app.serializers.hostel_admin import HostelAdminSerializer
from bhawan_app.constants import designations
from bhawan_app.managers.services import is_warden

Person = swapper.load_model('Kernel', 'Person')
Hostel = swapper.load_model('Kernel', 'Residence')

class HostelAdminViewset(viewsets.ModelViewSet):
    """
    CRUD views for getting admin information of all hostels
    """

    serializer_class = HostelAdminSerializer
    allowed_methods = ['GET', 'POST', 'PATCH',]

    def get_queryset(self):
        """
        Return the queryset of profile grouped by a hostel
        :return: the queryset of profile grouped by a hostel
        """
        filters = self.get_filters(self.request)
        queryset = HostelAdmin.objects.filter(**filters)
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
        if is_warden(request.person):
            try:
                data = request.data
                serializer = self.get_serializer(data=data)
                designation = request.data['designation']
                serializer.is_valid(raise_exception=True)
                person = Person.objects.get(pk=data['person'])
                today = date.today()
                hostel = Hostel.objects.get(code=hostel__code)
                is_resident = Resident.objects.filter(person=person).exists()

                """
                1. A resident can't hold administrative any posts.
                2. Can't hold any position in any other hostel than the
                   one he's residing in.
                """
                if is_resident:
                    if designation in designations.ADMINISTRATIVE_COUNCIL_LIST:
                        return Response(
                            "Resident of a hostel can't hold Administrative positions",
                            status=status.HTTP_403_FORBIDDEN,
                        )
                    hostel_code = person.resident.hostel.code
                    if hostel_code != hostel__code:
                        return Response(
                            f"Person {person.full_name} is not a resident of {hostel__code}",
                            status=status.HTTP_403_FORBIDDEN,
                        )
                
                if designation in designations.STUDENT_COUNCIL_LIST and not resident:
                    return Response(
                        f"Person {person.full_name} is not a registered resident",
                        status=status.HTTP_403_FORBIDDEN,
                    )

                
                serializer.save(
                    person=person,
                    start_date=today,
                    hostel=hostel,
                )
                
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
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
        if is_warden(request.person):
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

        return Response(
            'Only warden is allowed to perform this action !',
            status=status.HTTP_403_FORBIDDEN,
        )