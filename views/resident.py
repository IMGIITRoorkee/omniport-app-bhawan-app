import swapper
import pandas as pd

from datetime import datetime
from distutils.util import strtobool

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

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
        hostel_code = self.kwargs['hostel__code']
        if is_warden(request.person, hostel_code) or is_supervisor(request.person, hostel_code):
            pass
        else:
            raise PermissionDenied(
                "Only Supervisor and Warden are allowed to perform this action!",
            )

    def get_queryset(self):
        params = self.request.GET
        queryset = Resident.objects.filter(is_resident = True)
        queryset = self.apply_filters(self.request, queryset)
        return queryset

    def create(self, request, hostel__code):
        data = request.data
        try:
            person_id = data['person']
            room_number = data['room_number']
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
        fathers_name = None
        fathers_contact = None
        try:
            fathers_name = data['fathers_name']
            fathers_contact = data['fathers_contact']
        except:
            pass

        mothers_name = None
        mothers_contact = None
        try:
            mothers_name = data['mothers_name']
            mothers_contact = data['mothers_contact']
        except:
            pass

        father = None
        mother = None
        try:
            existing = Resident.objects.get(person=person)
            try:
                father = existing.father
                if(fathers_name is not None):
                    father.full_name = fathers_name
                    father.save()
                else:
                    father.delete()
                    father = None
            except:
                if(fathers_name is not None):
                    father = Person.objects.create(
                        full_name = fathers_name
                    )
                else:
                    father = None
            try:
                mother = existing.mother
                if(mothers_name is not None):
                    mother.full_name = mothers_name
                    mother.save()
                else:
                    mother.delete()
                    mother = None
            except:
                if(mothers_name is not None):
                    mother = Person.objects.create(
                        full_name = mothers_name
                    )
                else:
                    mother = None

            existing.delete()

        except Resident.DoesNotExist:
            if(fathers_name is not None):
                father = Person.objects.create(
                    full_name = fathers_name
                )
            if(mothers_name is not None):
                mother = Person.objects.create(
                    full_name = mothers_name
                )
        instance = Resident.objects.create(
            person=person,
            room_number=room_number,
            hostel=hostel,
            father=father,
            fathers_contact=fathers_contact,
            mother=mother,
            is_resident=True,
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

    @action(detail=True, methods=['get'])
    def deregister(self, request, hostel__code, pk):
        """
        This method deregisters a student from the Bhawan
        """
        try:
            person = Person.objects.get(pk=pk)
            hostel = Residence.objects.get(code=hostel__code)
            resident = Resident.objects.get(person=person, hostel=hostel, is_resident=True)
            resident.is_resident = False
            resident.save()
            return Response(
                f"{person.full_name} succesfully deregistered from {hostel__code}"
            )

        except Person.DoesNotExist:
            error = {
                "error": "There is no such person on Channeli"
            }
            return Response(
                error,
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Resident.DoesNotExist:
            error = {
                "error": f"{person.full_name} is not a resident of {hostel__code}"
            }
            return Response(
                error,
                status=status.HTTP_400_BAD_REQUEST,
            )



    @action(detail=False, methods=['get'])
    def download(self, request, hostel__code):
        """
        This method exports a csv corresponding to the list
        of students
        """
        params = self.request.GET
        queryset = Resident.objects.filter(is_resident = True)
        queryset = self.apply_filters(self.request, queryset)
        data = {
            'Enrolment No.': [],
            'Name': [],
            'Room No.': [],
            'Contact No': [],
            'Email': [],
            'Current Year': [],
            'Department': [],
            'Date of Birth': [],
            'Address': [],
            'City': [],
            'State': [],
            'Country': [],
            'Postal Code': [],
            'display_picture': [],
        }
        for resident in queryset:
            try:
                data['Enrolment No.'].append(self.get_enrolment_number(resident))
                data['Name'].append(resident.person.full_name)
                data['Room No.'].append(resident.room_number)
                data['Contact No'].append(self.get_phone_number(resident))
                data['Email'].append(self.get_email_address(resident))
                data['Current Year'].append(self.get_current_year(resident))
                data['Department'].append(self.get_department(resident))
                data['Date of Birth'].append(self.get_date_of_birth(resident))
                data['Address'].append(self.get_address(resident))
                data['City'].append(self.get_city(resident))
                data['State'].append(self.get_state(resident))
                data['Country'].append(self.get_country(resident))
                data['Postal Code'].append(self.get_postal_code(resident))
                data['display_picture'].append(resident.person.display_picture)
            except IndexError:
                pass

        file_name = f'{hostel__code}_students_list.csv'
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        df.to_csv(path_or_buf=response, index=False)
        return response

    def get_enrolment_number(self, resident):
        """
        Retrives the enrolment number of a resident
        if he is a student
        """
        try:
            student = Student.objects.get(person=resident.person)
            return student.enrolment_number
        except Student.DoesNotExist:
            return None

    def get_email_address(self, resident):
        """
        Retrieves the email address for a resident.
        """
        try:
            contact_information = \
                ContactInformation.objects.get(person=resident.person)
            return contact_information.email_address
        except ContactInformation.DoesNotExist:
            return None

    def get_current_year(self, resident):
        """
        Retrives the current year of a resident
        if he is a student
        """
        try:
            student = Student.objects.get(person=resident.person)
            return student.current_year
        except Student.DoesNotExist:
            return None

    def get_department(self, resident):
        """
        Retrives the department of a resident
        if he is a student
        """
        try:
            student = Student.objects.get(person=resident.person)
            branch = Branch.objects.get(student=student)
            return branch.name
        except Student.DoesNotExist:
            return None
        except Branch.DoesNotExist:
            return None

    def get_phone_number(self, resident):
        """
        Retrives the phone number of a resident
        if he is a student
        """
        try:
            contact_information = \
                ContactInformation.objects.get(person=resident.person)
            return contact_information.primary_phone_number
        except ContactInformation.DoesNotExist:
            return None

    def get_date_of_birth(self, resident):
        """
        Retrives the date of birth of a resident
        if he is a student
        """
        try:
            biological_information = \
                BiologicalInformation.objects.get(person=resident.person)
            return biological_information.date_of_birth
        except BiologicalInformation.DoesNotExist:
            return None

    def get_address(self, resident):
        """
        Retrives the address of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.get(person=resident.person)
            return location_information.address
        except LocationInformation.DoesNotExist:
            return None

    def get_city(self, resident):
        """
        Retrives the city of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.get(person=resident.person)
            return location_information.city
        except LocationInformation.DoesNotExist:
            return None

    def get_state(self, resident):
        """
        Retrives the state of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.get(person=resident.person)
            return location_information.state
        except LocationInformation.DoesNotExist:
            return None

    def get_country(self, resident):
        """
        Retrives the address of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.get(person=resident.person)
            return location_information.country.name
        except LocationInformation.DoesNotExist:
            return None

    def get_postal_code(self, resident):
        """
        Retrives the address of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.get(person=resident.person)
            return location_information.postal_code
        except LocationInformation.DoesNotExist:
            return None
