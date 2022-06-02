import swapper
from django.db import models
from django.core.validators import MaxValueValidator
from django.dispatch import receiver

from formula_one.models.base import Model
from bhawan_app.constants import room_types,room_occupancy
# from bhawan_app.utils.notification.push_notification import send_push_notification


class Room(Model):
    """
    Describes the room
    """
    hostel = models.ForeignKey(
        to=swapper.get_model_name("kernel", "Residence"),
        on_delete=models.CASCADE,
        null=True
    )
    room_type = models.CharField(
        max_length=15,
        choices=room_types.ROOM_TYPES,
        default=room_types.TOTAL,
    )
    occupancy = models.CharField(
        max_length=15,
        choices=room_occupancy.ROOM_OCCUPANCY,
        default=room_occupancy.SINGLE,
    )
    count = models.PositiveIntegerField(
        default=0,
    )


    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        room_type = self.get_room_type_display()
        occupancy = self.get_occupancy_display()
        hostel = self.hostel
        count = self.count
        return f"{count} {occupancy} {room_type} in {hostel}"

