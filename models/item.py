import swapper
from django.db import models
from django.core.validators import MaxValueValidator
from django.dispatch import receiver

from formula_one.models.base import Model
from bhawan_app.constants import complaint_items
from bhawan_app.models.complaint import Complaint
from bhawan_app.models.default_item import DefaultItem
# from bhawan_app.utils.notification.push_notification import send_push_notification


class Item(Model):
    """
    Describes the details of the item replaced/repaired
    """

    complaint = models.ForeignKey(
        to=Complaint,
        on_delete=models.CASCADE,
    )
    default_item = models.ForeignKey(
        to=DefaultItem,
        on_delete=models.CASCADE,
        related_name='item_name',
    )
    quantity = models.PositiveIntegerField(
        default=0,
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        name = self.default_item.name
        quantity = self.quantity
        complaint = self.complaint.description
        return f"{quantity} {name} according to complaint {complaint}"

