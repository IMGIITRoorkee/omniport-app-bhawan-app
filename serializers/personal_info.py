import swapper

from rest_framework import serializers

from kernel.managers.get_role import get_role
from formula_one.mixins.period_mixin import ActiveStatus

from bhawan_app.managers.services import get_hostel_admin
from bhawan_app.models import Resident, HostelAdmin



class PersonalInfoSerializer(serializers.Serializer):
    """
    Serializer for personal information of student related to bhawans"
    """

    hostel = serializers.SerializerMethodField(
        read_only=True,
    )
    room_number = serializers.SerializerMethodField(
        read_only=True
    )
    is_admin = serializers.SerializerMethodField(
        read_only=True,
    )
    is_student = serializers.SerializerMethodField(
        read_only=True,
    )
    full_name = serializers.CharField(
        source='person.full_name',
    )
    id = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for PersonalInfoSerializer
        """
        fields = [
            'id',
            'is_admin',
            'full_name',
            'hostel',
            'room_number',
            'is_student',
            'room_number'
        ]

    def get_hostel(self, obj):
        """
        Returns a list of hostels a person is associated with
        :param obj: an instance of HostelAdmin or Resident
        :return: a unique identification ID for the logged in person
        """
        hostel_list = []
        if isinstance(obj, HostelAdmin):
            hostel_list = HostelAdmin.objects\
                .filter(person=obj.person).values_list('hostel__code', flat=True)
        else:
            hostel_list = [obj.hostel.code]
        return hostel_list


    def get_room_number(self, obj):
        """
        Returns the room number of person
        """
        try:
            resident = Resident.objects.get(person = obj.person)
            return resident.room_number
        except Resident.DoesNotExist:
            return None


    def get_id(self, obj):
        """
        Returns a unique identification ID for the logged in person
        :param obj: an instance of HostelAdmin or Resident
        :return: a unique identification ID for the logged in person
        """

        role_student = get_role(
            person=obj.person,
            role_name='Student',
            active_status=ActiveStatus.IS_ACTIVE,
            silent=True,
        )
        role_faculty_member = get_role(
            person=obj.person,
            role_name='FacultyMember',
            active_status=ActiveStatus.IS_ACTIVE,
            silent=True,
        )
        if role_student is not None:
            return obj.person.student.enrolment_number
        elif role_faculty_member is not None:
            return obj.person.facultymember.employee_id
        else:
            return obj.person.id

    def get_is_admin(self, obj):
        """
        Checks if the authenticated user is a hostel administrator or not
        :param obj: an instance of HostelAdmin or Resident
        :return: a boolean if the authenticated user is a hostel administrator
        or not
        """

        if get_hostel_admin(obj.person) is None:
            return False
        return True
    
    def get_is_student(self, obj):
        """
        Checks if the authenticated user is a student or not
        :param obj: an instance of ResidentialInformation
        :return: a boolean if the authenticated user is a student or not
        """

        role_student = get_role(
            person=obj.person,
            role_name='Student',
            active_status=ActiveStatus.IS_ACTIVE,
            silent=True,
        )
        return role_student is not None

    def get_is_resident(self, obj):
        """
        Checks if the authenticated user is a registered resident of any hostel or not
        """

        person = obj.person
        return Resident.objects.filter(person=person).exists()
