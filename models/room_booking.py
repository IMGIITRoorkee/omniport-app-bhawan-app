import swapper

from formula_one.models.base import Model
from django.db import models
from bhawan_app.constants import statuses
from bhawan_app.models.resident import Resident



class RoomBooking(Model):
    """
    Describes the details of a complaint registered.
    """

    resident = models.ForeignKey(
        to=Resident,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=10, 
        choices=statuses.BOOKING_STATUSES, 
        default=statuses.PENDING,
    )
    requested_from = models.DateField()
    requested_till = models.DateField()

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        return f"{self.resident.person.full_name}'s booking."
