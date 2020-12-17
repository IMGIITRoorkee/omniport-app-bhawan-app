import swapper

from rest_framework import serializers

from bhawan_app.models import Resident
from formula_one.models.generics.contact_information import ContactInformation

Student = swapper.load_model('Kernel', 'Student')
Branch = swapper.load_model('Kernel', 'Branch')
BiologicalInformation = swapper.load_model('Kernel', 'BiologicalInformation')


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
    email_address = serializers.SerializerMethodField()
    enrolment_number = serializers.SerializerMethodField()
    current_year = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    is_resident = serializers.ReadOnlyField(default=True)

    class Meta:
        model = Resident
        fields = [
            "id",
            "resident_name",
            "room_number",
            "hostel_code",
            "email_address",
            "enrolment_number",
            "current_year",
            "department",
            "phone_number",
            "date_of_birth",
            "is_resident",
            "display_picture"
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
                ContactInformation.objects.get(person=resident.person)
            return contact_information.email_address
        except ContactInformation.DoesNotExist:
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
        Retrives the dep of a resident
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
