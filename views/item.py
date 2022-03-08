from email.policy import default
import swapper
import json
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bhawan_app.models import Item, Complaint, DefaultItem
from bhawan_app.serializers.item import ItemSerializer
from bhawan_app.managers.services import is_hostel_admin, is_global_admin, is_warden, is_supervisor
from bhawan_app.constants import complaint_items
from bhawan_app.pagination.custom_pagination import CustomPagination 

Residence = swapper.load_model('kernel', 'Residence')

class ItemViewset(viewsets.ModelViewSet):
    """
    Detail view for getting complaint item information of a single hostel
    """

    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated,]
    allowed_methods = ['GET', 'POST', 'PATCH']
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Return the queryset of complaint items of a hostel
        :return: the queryset of complaint items of a hostel
        """

        hostel = self.kwargs['hostel__code']
        queryset = Item.objects.filter(complaint__resident__hostel__code=hostel)
        data = {}
        result = []
        for d in queryset:
            if d.default_item in data.keys():
                data[d.default_item]+=d.quantity
            else:
                data[d.default_item]=d.quantity
        for default_item,quantity in data.items():
            result.append({
                'default_item' : default_item,
                'quantity' : quantity
            })
        return result


    def create(self, request, hostel__code):
        """
        Create item instance if user has required permissions.
        :return: status code of the request
        """

        if not is_global_admin(request.person) and not is_hostel_admin(request.person, hostel__code) and not is_warden(request.person, hostel__code) and not is_supervisor(request.person, hostel__code):
            return Response(
            {"You are not allowed to perform this action !"},
            status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        default_item_id = data.get('default_item', None)
        quantity = data.get('quantity', None)
        complaint_id = data.get('complaint', None)
            
        try:
            default_item = DefaultItem.objects.get(id=default_item_id)
        except DefaultItem.DoesNotExist:
            return Response(
                "Default Item doesn't exist !",
                status.HTTP_404_NOT_FOUND,
            )
            
        try:
            complaint = Complaint.objects.get(id=complaint_id)
        except Complaint.DoesNotExist:
            return Response(
                "Complaint doesn't exist !",
                status.HTTP_404_NOT_FOUND,
            )
        
        instance = Item.objects.create(
            complaint=complaint,
            default_item=default_item,
            quantity=quantity,
            datetime_modified=datetime.now(),
        )
        return Response(ItemSerializer(instance).data, status=status.HTTP_201_CREATED)

    