import swapper
from django.db import models
from formula_one.models.base import Model


class Resident(Model):
    """
    Describes the details of a registered Resident.
    """

    person = models.OneToOneField(
        to=swapper.get_model_name("Kernel", "Person"), on_delete=models.CASCADE,
    )
    hostel = models.ForeignKey(
        to=swapper.get_model_name("kernel", "Residence"),
        on_delete=models.PROTECT,
    )
    room_number = models.CharField(
        max_length=10,
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        room_no = self.room_number
        hostel = self.hostel.name
        person = self.person
        return f"{person} - {hostel}({room_no})"
