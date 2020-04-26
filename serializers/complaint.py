import swapper
from datetime import datetime

from rest_framework import serializers

from formula_one.models.generics.contact_information import ContactInformation
from bhawan_app.models import Complaint, ComplaintTimeSlot
from bhawan_app.serializers.timing import TimingSerializer
from bhawan_app.constants import statuses


class ComplaintSerializer(serializers.ModelSerializer):
    """
    Serializer for Complaint objects
    """

    def __init__(self, *args, **kwargs):
        """If object is being updated don't allow contact to be changed."""
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields.get('status').read_only = False

    complainant = serializers.CharField(
        source='person.full_name',
        read_only=True,
    )
    hostel_code = serializers.CharField(
        source='person.residentialinformation.residence.code',
        read_only=True,
    )
    room_no = serializers.CharField(
        source='person.residentialinformation.room_number',
        read_only=True,
    )

    phone_number = serializers.SerializerMethodField()

    timing = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = [
            "complainant",
            "status",
            "complaint_type",
            "room_no",
            "hostel_code",
            "description",
            "id",
            "phone_number",
            "timing",
            "failed_attempts",
            "datetime_created"
        ]
        extra_kwargs = {
            "status": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data["person"] = self.context["person"]
        validated_data["status"] = statuses.PENDING
        validated_data["datetime_modified"] = datetime.now()
        return super().create(validated_data)

    def get_timing(self, obj):
        """
        Returns the timings of a complaint type.
        :return: Timing of a complaint
        """

        try:
            hostel = obj.person.residentialinformation.residence
            timings = ComplaintTimeSlot.objects\
                .filter(hostel=hostel).get(complaint_type=obj.complaint_type)
            new_timings = timings.timing.all()
            return TimingSerializer(new_timings, many=True).data
        except ComplaintTimeSlot.DoesNotExist:
            return None

    def get_phone_number(self, obj):
        """
        Returns the timings of a complaint.
         Returns the primary phone number of the complainant
        :return: the primary phone number of the complainant
        """

        try:
            contact_information = \
                ContactInformation.objects.get(person=obj.person)
            return contact_information.primary_phone_number
        except ContactInformation.DoesNotExist:
            return None
