import swapper

from rest_framework import serializers

from bhawan_app.models import DefaultItem


class DefaultItemSerializer(serializers.ModelSerializer):
    """
    Serializer for DefaultItem objects
    """
    
    class Meta:
        model = DefaultItem
        fields = [
            "name",
            "id",
            "datetime_created",
        ]
