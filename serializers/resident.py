import swapper

from rest_framework import serializers

from bhawan_app.models import Resident


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

    class Meta:
        model = Resident
        fields = [
            "id",
            "resident_name",
            "room_number",
            "hostel_code",
        ]
