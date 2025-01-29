import swapper
import pandas as pd

from datetime import datetime
from distutils.util import strtobool

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
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
    is_hostel_admin,
    is_global_admin,
)
from bhawan_app.pagination.custom_pagination import CustomPagination


Person = swapper.load_model("Kernel", "Person")
Residence = swapper.load_model("kernel", "Residence")
Student = swapper.load_model('Kernel', 'Student')
Branch = swapper.load_model('Kernel', 'Branch')
BiologicalInformation = swapper.load_model('Kernel', 'BiologicalInformation')
PoliticalInformation = swapper.load_model('kernel', 'PoliticalInformation')

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
        if is_warden(request.person, hostel_code) or is_supervisor(request.person, hostel_code) or is_global_admin(request.person):
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
            start_date = data['start_date']
            fee_type = data['fee_type']
            address_bhawan=data['address_bhawan']
            admission_date=data['admission_date']
            contact_number_as_bhawan=data['contact_number_as_bhawan']
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
            
        is_living_in_campus = True
        try:
            is_living_in_campus = data['is_living_in_campus']
        except:
            pass

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
            existing = Resident.objects.get(person=person, is_resident=True)
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

            existing.is_resident = False
            existing.end_date = datetime.now()
            existing.save()

        except Resident.DoesNotExist:
            if(fathers_name is not None):
                father = Person.objects.create(
                    full_name = fathers_name
                )
            if(mothers_name is not None):
                mother = Person.objects.create(
                    full_name = mothers_name
                )

        adm_date = None
        if not (admission_date == "Invalid date" or admission_date == ""):
            adm_date = admission_date
            
        instance = Resident.objects.create(
            person=person,
            room_number=room_number,
            start_date=start_date,
            hostel=hostel,
            fee_type=fee_type,
            is_living_in_campus=is_living_in_campus,
            father=father,
            fathers_contact=fathers_contact,
            mother=mother,
            is_resident=True,
            mothers_contact=mothers_contact,
            address_bhawan=address_bhawan,
            admission_date=adm_date,
            contact_number_as_bhawan=contact_number_as_bhawan,
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
            obj["reservation_category"] = None
            obj["is_living_in_campus"] = False
            obj["address_bhawan"]=None
            obj["admission_date"]=None
            obj["contact_number_as_bhawan"]=None

            try:
                contact_information = \
                    ContactInformation.objects.filter(person=person).first()
                if(contact_information):
                    obj["email_address"] = contact_information.institute_webmail_address
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
                category_information = \
                    PoliticalInformation.objects.get(person=person)
                obj["reservation_category"] = category_information.reservation_category
            except PoliticalInformation.DoesNotExist:
                obj["reservation_category"] = None


            try:
                location_information = \
                    LocationInformation.objects.filter(person=person).first()
                if(location_information):
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
                obj["program"] = [branch.name, branch.degree.name]
                obj["department"] = branch.department.name
                obj["current_year"] = student.current_year
                obj["current_semester"] = student.current_semester
            except Student.DoesNotExist:
                obj["program"] = None
                obj["department"] = None
                obj["current_year"] = None
                obj["current_semester"] = None
            except Branch.DoesNotExist:
                obj["program"] = None
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
            instance = Resident.objects.get(
                person__student__enrolment_number=enrolment_number,
                is_resident=True,
            )
        except Resident.DoesNotExist:
            return Response(
                "Resident with this enrolment number doesn't exist !",
                status=status.HTTP_404_NOT_FOUND,
            )

        if "room_number" in data:
            instance.room_number = data.get("room_number")

        if "start_date" in data:
            instance.start_date = data.get("start_date")

        if "is_living_in_campus" in data:
            instance.is_living_in_campus = data.get("is_living_in_campus")

        if "fathers_contact" in data:
            instance.fathers_contact = data.get("fathers_contact")
        
        if "mothers_contact" in data:
            instance.mothers_contact = data.get("mothers_contact")

        if "fee_type" in data:
            instance.fee_type = data.get("fee_type")
    
        if "address_bhawan" in data:
            instance.address_bhawan = data.get("address_bhawan")
    

        if "admission_date" in data:
            adm_date = None
            admission_date = data.get("admission_date")
            if not (admission_date == "" or admission_date == "Invalid date"):
                adm_date = admission_date                
            instance.admission_date = adm_date

        if "contact_number_as_bhawan" in data:
            instance.contact_number_as_bhawan = data.get("contact_number_as_bhawan")


        instance.save()
        return Response(ResidentSerializer(instance).data)

    def apply_filters(self, request, queryset):
        """
        Return a dict with all the filters populated with the
        filters received from query params.
        """
        filters = {}
        search_query = Q()
        params = self.request.GET

        """
        Filter based on the fact, if person is resident
        """
        is_resident = strtobool(params.get('is_resident', 'true'))

        """
        Filter based on feetype
        """
        fee_type = params.get('feeType', None)
        if fee_type:
            filters['fee_type'] = fee_type

        """
        Filter based on search(Name/Enrollment no.)
        """
        search = params.get('search',"")
        if len(search):
            search_query = Q(person__student__enrolment_number__contains=search) | Q(person__full_name__icontains=search)

        """
        Filter based on hostel
        """
        if not params.get('all') and is_resident:
            filters['hostel__code'] = self.kwargs['hostel__code']

        """
        Filter based on Year
        """
        year = params.get('year', None)
        
        if year:
            year_array = year.split(',')
            filters['person__student__current_year__in'] = year_array

        is_living_in_campus = params.get('is_living_in_campus', None)
        if is_living_in_campus:
            filters['is_living_in_campus'] = is_living_in_campus

        """
        Filter based on Semester
        """
        semester = params.get('semester', None)
        
        if semester:
            semester_array = semester.split(',')
            filters['person__student__current_semester__in'] = semester_array

        """
        Filter based on Department
        """
        department = params.get('department', None)
        if department:
            department_array = department.split(',')
            filters['person__student__branch__department__code__in'] = department_array

        """
        Filter based on Branch
        """
        branch = params.get('branch', None)
        if branch:
            branch_array = branch.split(',')
            filters['person__student__branch__code__in'] = branch_array

        """
        Filter based on Degree
        """
        degree = params.get('degree', None)
        if degree:
            degree_array = degree.split(',')
            filters['person__student__branch__degree__code__in'] = degree_array

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

        queryset = queryset.filter(**filters).filter(search_query).order_by('-datetime_created')

        if not is_resident:
            queryset = queryset.filter(id__in=queryset.order_by('person','-datetime_created').distinct('person').values('id')).filter(is_resident=is_resident)

        queryset = queryset.filter(is_resident=is_resident)
        return queryset

    @action(detail=True, methods=['get'])
    def previous_records(self, request, hostel__code, pk):
        """
        This method gives all records of a student
        """
        try:
            person = Person.objects.get(student__enrolment_number=pk)
            residents = Resident.objects.filter(person=person)
            prev_records = []
            for resident in residents:
                record = {
                    "start_date": resident.start_date,
                    "end_date": resident.end_date,
                    "hostel": resident.hostel.code
                }
                prev_records.append(record)
            return Response(prev_records)

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
            resident.end_date = datetime.now()
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


    @action(detail = True, methods=['get'])
    def markin(self, request, hostel__code, pk):
        """
        This method marks a student in the campus
        """
        try:
            person = Person.objects.get(pk=pk)
            hostel = Residence.objects.get(code=hostel__code)
            resident = Resident.objects.get(person=person, hostel=hostel, is_resident=True)
            resident.is_living_in_campus = True
            resident.save()
            return Response(
                f"{person.full_name} succesfully marked inside {hostel__code}"
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

    
    @action(detail = True, methods=['get'])
    def markout(self, request, hostel__code, pk):
        """
        This method marks a student out of campus
        """
        try:
            person = Person.objects.get(pk=pk)
            hostel = Residence.objects.get(code=hostel__code)
            resident = Resident.objects.get(person=person, hostel=hostel, is_resident=True)
            resident.is_living_in_campus = False
            resident.save()
            return Response(
                f"{person.full_name} succesfully marked out of {hostel__code}"
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
        queryset = Resident.objects.all()
        queryset = self.apply_filters(self.request, queryset)
        data = {
            'Enrolment No.': [],
            'Name': [],
            'Hostel': [],
            'Room No.': [],
            'Contact No': [],
            'Email': [],
            'Fee Status': [],
            'Inside Campus': [], 
            'Current Year': [],
            'Program': [],
            'Department': [],
            'Fathers Name': [],
            'Fathers Contact': [],
            'Mothers Name': [],
            'Mothers Contact': [],
            'Degree': [],
            'Date of Birth': [],
            'Address':[],
            'Student Home Address as per Bhawan Records': [],
            'Admission Date':[],
            'Contact Number As Per Bhawan Records':[],
            'City': [],
            'State': [],
            'Country': [],
            'Postal Code': [],
            'Reservation Category': [],
        }
        for resident in queryset:
            try:
                data['Enrolment No.'].append(self.get_enrolment_number(resident))
                data['Name'].append(resident.person.full_name)
                data['Room No.'].append(resident.room_number)
                data['Hostel'].append(resident.hostel.name)
                data['Contact No'].append(self.get_phone_number(resident))
                data['Email'].append(self.get_email_address(resident))
                data['Fee Status'].append(resident.fee_type)
                if(resident.father):
                    data['Fathers Name'].append(resident.father.full_name)
                    data['Fathers Contact'].append(resident.fathers_contact)
                else:
                    data['Fathers Name'].append("")
                    data['Fathers Contact'].append("")
                if(resident.mother):
                    data['Mothers Name'].append(resident.mother.full_name)
                    data['Mothers Contact'].append(resident.mothers_contact)
                else:
                    data['Mothers Name'].append("")
                    data['Mothers Contact'].append("")
                data['Current Year'].append(self.get_current_year(resident))
                data['Current Semester'].append(self.get_current_semester(resident))

                program = self.get_program(resident)
                data['Degree'].append(program[1])
                data['Program'].append(program[0])

                data['Department'].append(self.get_department(resident))
                data['Date of Birth'].append(self.get_date_of_birth(resident))
                data['Address'].append(self.get_address(resident))
                data['Student Home Address as per Bhawan Records'].append(resident.address_bhawan)
                data['Admission Date'].append(resident.admission_date)
                data['Contact Number As Per Bhawan Records'].append(resident.contact_number_as_bhawan)
                data['City'].append(self.get_city(resident))
                data['State'].append(self.get_state(resident))
                data['Country'].append(self.get_country(resident))
                data['Postal Code'].append(self.get_postal_code(resident))
                data['Reservation Category'].append(self.get_reservation_category(resident))
                if (resident.is_living_in_campus):
                    data['Inside Campus'].append("Yes")
                else:
                    data['Inside Campus'].append("No")
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
                ContactInformation.objects.filter(person=resident.person).first()
            if(contact_information):
                return contact_information.institute_webmail_address
        except ContactInformation.DoesNotExist:
            return None
        return None

    def get_reservation_category(self, resident):
        try:
            category_information = \
                PoliticalInformation.objects.get(person=resident.person)
            return category_information.reservation_category
        except PoliticalInformation.DoesNotExist:
            return None
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
        return None
    
    def get_current_semester(self, resident):
        """
        Retrives the current semester of a resident
        if he is a student
        """
        try:
            student = Student.objects.get(person=resident.person)
            return student.current_semester
        except Student.DoesNotExist:
            return None
        return None


    def get_program(self, resident):
        """
        Retrives the program of a resident
        if he is a student
        """
        try:
            student = Student.objects.get(person=resident.person)
            branch = Branch.objects.get(student=student)
            return [branch.name, branch.degree.name]
        except Student.DoesNotExist:
            return [None, None]
        except Branch.DoesNotExist:
            return [None, None]
        return [None, None]
    
    def get_department(self, resident):
        """
        Retrives the department of a resident
        if he is a student
        """
        try:
            student = Student.objects.get(person=resident.person)
            branch = Branch.objects.get(student=student)
            return branch.department.name
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
                ContactInformation.objects.filter(person=resident.person).first()
            if(contact_information):
                return contact_information.primary_phone_number
        except ContactInformation.DoesNotExist:
            return None
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
        return None

    def get_address(self, resident):
        """
        Retrives the address of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.filter(person=resident.person).first()
            if(location_information):
                return location_information.address
        except LocationInformation.DoesNotExist:
            return None
        return None

    def get_city(self, resident):
        """
        Retrives the city of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.filter(person=resident.person).first()
            if(location_information):
                return location_information.city
        except LocationInformation.DoesNotExist:
            return None
        return None

    def get_state(self, resident):
        """
        Retrives the state of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.filter(person=resident.person).first()
            if(location_information):
                return location_information.state
        except LocationInformation.DoesNotExist:
            return None
        return None

    def get_country(self, resident):
        """
        Retrives the address of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.filter(person=resident.person).first()
            if(location_information):
                return location_information.country.name
        except LocationInformation.DoesNotExist:
            return None
        return None

    def get_postal_code(self, resident):
        """
        Retrives the address of the resident
        """
        try:
            location_information = \
                LocationInformation.objects.filter(person=resident.person).first()
            if(location_information):
                return location_information.postal_code
        except LocationInformation.DoesNotExist:
            return None
        return None
