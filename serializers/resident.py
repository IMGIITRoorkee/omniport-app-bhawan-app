import swapper

from django_countries.serializer_fields import CountryField

from rest_framework import serializers

from bhawan_app.models import Resident
from formula_one.models.generics.contact_information import ContactInformation
from formula_one.models.generics.location_information import LocationInformation

Student = swapper.load_model('Kernel', 'Student')
Branch = swapper.load_model('Kernel', 'Branch')
BiologicalInformation = swapper.load_model('Kernel', 'BiologicalInformation')
PoliticalInformation = swapper.load_model('kernel', 'PoliticalInformation')


class ResidentSerializer(serializers.ModelSerializer):
    """
    Serializer for Resident objects
    """

    resident_name = serializers.CharField(
        source='person.full_name',
        read_only=True,
    )
    hostel_code = serializers.CharField(
        source='hostel.code',
        read_only=True,
    )
    display_picture = serializers.ImageField(
        source='person.display_picture',
        read_only=True,
    )
    fathers_name = serializers.CharField(
        source='father.full_name',
        read_only=True,
    )
    mothers_name = serializers.CharField(
        source='mother.full_name',
        read_only=True,
    )
    email_address = serializers.SerializerMethodField()
    enrolment_number = serializers.SerializerMethodField()
    current_year = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    is_resident = serializers.ReadOnlyField(default=True)
    address = serializers.SerializerMethodField()
    address_bhawan=serializers.SerializerMethodField()
    registration_date=serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    postal_code = serializers.SerializerMethodField()
    reservation_category = serializers.SerializerMethodField()

    class Meta:
        model = Resident
        fields = [
            "id",
            "resident_name",
            "room_number",
            "is_living_in_campus",
            "fee_type",
            "start_date",
            "end_date",
            "hostel_code",
            "email_address",
            "enrolment_number",
            "current_year",
            "department",
            "phone_number",
            "date_of_birth",
            "is_resident",
            "display_picture",
            "address",
            "address_bhawan",
            "registration_date",
            "city",
            "state",
            "country",
            "postal_code",
            "fathers_name",
            "fathers_contact",
            "mothers_name",
            "mothers_contact",
            "reservation_category",
        ]
        extra_kwargs = {
            'room_number': { 'read_only': True },
        }

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

    def get_reservation_category(self, resident):
        try:
            category_information = \
                PoliticalInformation.objects.get(person=resident.person)
            return category_information.reservation_category
        except PoliticalInformation.DoesNotExist:
            return None

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
            return [branch.name, branch.degree.name]
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
