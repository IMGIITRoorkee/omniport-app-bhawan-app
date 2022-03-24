import swapper

from rest_framework import serializers

from bhawan_app.models import Item
from bhawan_app.serializers.default_item import DefaultItemSerializer


class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for Item objects
    """

    hostel_code = serializers.CharField(
        source='complaint.resident.hostel.code',
        read_only=True,
    )

    name = serializers.ReadOnlyField(source='default_item.name')                     

    
    class Meta:
        model = Item
        fields = [
            "name",
            "quantity",
            "hostel_code",
            "id",
            "datetime_created",
        ]
