from rest_framework.serializers import ModelSerializer
from bhawan_app.models import HostelRoomBooking
from bhawan_app.serializers import HostelVisitorSerializer

class HostelRoomBookingSerializer(ModelSerializer):
    """
    Serializer for HostelRoomBooking objects
    """

    visitor_details = HostelVisitorSerializer(many=True)

    class Meta:
        """
        Meta class for HostelRoomBookingSerializer
        """

        model = HostelRoomBooking
        fields = [
            'time_of_booking',
            'from_date',
            'to_date',
            'number_of_rooms',
            'visitor_details',
            'booking_status',
        ]