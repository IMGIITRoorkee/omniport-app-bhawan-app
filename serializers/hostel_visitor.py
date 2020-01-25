from rest_framework.serializers import ModelSerializer
from bhawan_app.models import HostelVisitor

class HostelVisitorSerializer(ModelSerializer):
    """
    Serializer class for HostelVisitor object
    """

    class Meta:
        """
        Meta class for HostelVisitorSerializer
        """

        model = HostelVisitor
        fields = [
            'visitor_name',
            'visitor_relation',
        ] 