import swapper
from django.db import models
from django.core.validators import MaxValueValidator

from formula_one.models.base import Model
from bhawan_app.constants import complaint_types, statuses
from bhawan_app.models.complaint_time_slot import ComplaintTimeSlot
from bhawan_app.models.resident import Resident



class Complaint(Model):
    """
    Describes the details of a complaint registered.
    """

    resident = models.ForeignKey(
        to=Resident,
        on_delete=models.CASCADE,
    )
    complaint_type = models.CharField(
        max_length=10,
        choices=complaint_types.COMPLAINT_TYPES,
        default=complaint_types.OTHER,
    )

    status = models.CharField(
        max_length=10, choices=statuses.COMLAINT_STATUSES, default=statuses.PENDING
    )
    description = models.TextField()
    failed_attempts = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(3)],
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        complaint_type = self.get_complaint_type_display()
        room_no = self.resident.room_number
        return f"{complaint_type} issue in {room_no}"
