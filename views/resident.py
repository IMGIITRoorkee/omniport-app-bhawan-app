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

from formula_one.models.generics.contact_information import ContactInformation
from formula_one.models.generics.location_information import LocationInformation
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
Student = swapper.load_model('Kernel', 'Student')
Branch = swapper.load_model('Kernel', 'Branch')
BiologicalInformation = swapper.load_model('Kernel', 'BiologicalInformation')

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
            having_computer = data['having_computer']
            fathers_name = data['fathers_name']
            fathers_contact = data['fathers_contact']
            mothers_name = data['mothers_name']
            mothers_contact = data['mothers_contact']
        except Exception:
            return Response(
                "Invalid field values for invalid input",
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
            try:
                father = existing.father
                father.full_name = fathers_name
                father.save()
            except:
                father = Person.objects.create(
                    full_name = fathers_name
                )
            try:
                mother = existing.mother
                mother.full_name = mothers_name
                mother.save()
            except:
                mother = Person.objects.create(
                    full_name = mothers_name
                )
            existing.delete()
        except Resident.DoesNotExist:
            father = Person.objects.create(
                full_name = fathers_name
            )
            mother = Person.objects.create(
                full_name = mothers_name
            )
        instance = Resident.objects.create(
            person=person,
            room_number=room_number,
            having_computer=having_computer,
            hostel=hostel,
            father=father,
            fathers_contact=fathers_contact,
            mother=mother,
            mothers_contact=mothers_contact,
        )
        return Response(ResidentSerializer(instance).data)

    def retrieve(self, request, hostel__code, pk=None):
        enrolment_number = pk
        try:
            queryset = self.get_queryset()
            instance = queryset.get(person__student__enrolment_number=enrolment_number)
            return Response(ResidentSerializer(instance).data)

        except Resident.DoesNotExist:
            person = Person.objects.get(student__enrolment_number=enrolment_number)
            obj = {}
            obj["enrolment_number"] = enrolment_number
            obj["resident_name"] = person.full_name
            try:
                obj["display_picture"] = person.display_picture.url
            except:
                obj["display_picture"] = None
            obj["hostel_code"] = None
            obj["is_resident"] = False
            obj["address"] = None
            obj["city"] = None
            obj["state"] = None
            obj["country"] = None
            obj["postal_code"] = None

            try:
                contact_information = \
                    ContactInformation.objects.get(person=person)
                obj["email_address"] = contact_information.email_address
                obj["phone_number"] = contact_information.primary_phone_number
            except ContactInformation.DoesNotExist:
                obj["email_address"] = None
                obj["phone_number"] = None

            try:
                biological_information = \
                    BiologicalInformation.objects.get(person=person)
                obj["date_of_birth"] = biological_information.date_of_birth
            except BiologicalInformation.DoesNotExist:
                obj["date_of_birth"] = None

            try:
                location_information = \
                    LocationInformation.objects.get(person=person)
                obj["address"]=location_information.address,
                obj["city"]=location_information.city,
                obj["state"]=location_information.state,
                obj["country"]=location_information.country.name,
                obj["postal_code"]=location_information.postal_code
            except LocationInformation.DoesNotExist:
                obj["address"] = None
                obj["city"] = None
                obj["state"] = None
                obj["country"] = None
                obj["postal_code"] = None

            try:
                student = Student.objects.get(person=person)
                branch = Branch.objects.get(student=student)
                obj["department"] = branch.name
                obj["current_year"] = student.current_year
            except Student.DoesNotExist:
                obj["department"] = None
                obj["current_year"] = None
            except Branch.DoesNotExist:
                obj["department"] = None

            return Response(obj)

        except Person.DoesNotExist:
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

    @action(detail=False, methods=['get'])
    def download(self, request):
        """
        This method exports a csv corresponding to the list
        of students
        """
        pass
