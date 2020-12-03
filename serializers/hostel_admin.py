import swapper

from rest_framework import serializers

from bhawan_app.models.roles.hostel_admin import HostelAdmin
from formula_one.models.generics.contact_information import ContactInformation

Person = swapper.load_model('Kernel', 'Person')

class HostelAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for Visitor objects
    """

    name = serializers.CharField(
        source='person.full_name',
        read_only=True,
    )
    email_address = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    room_number = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class for ProfileSerializer
        """

        model = HostelAdmin
        fields = [
            'id',
            'designation',
            'name',
            'email_address',
            'phone_number',
            'room_number',
        ]

    def get_email_address(self, admin):
        """
        Retrieves the email address for an Admin.
        """
        try:
            contact_information = \
                ContactInformation.objects.get(person=admin.person)
            return contact_information.email_address
        except ContactInformation.DoesNotExist:
            return None
    
    def get_phone_number(self, obj):
        """
        Returns the phone number of an admin.
         Returns the primary phone number of the admin
        :return: the primary phone number of the admin
        """

        try:
            contact_information = \
                ContactInformation.objects.get(person=obj.person)
            return contact_information.primary_phone_number
        except ContactInformation.DoesNotExist:
            return None
    
    def get_room_number(self, obj):
        """
        Returns the room number of admin.
         Returns the primary room number of the admin
        :return: the primary room number of the admin
        """
        person = obj.person
        if hasattr(person, 'resident'):
            return person.resident.room_number
        return None