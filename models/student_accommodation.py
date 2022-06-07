import swapper
from django.db import models
from django.dispatch import receiver

from formula_one.models.base import Model


class StudentAccommodation(Model):
    """
    Describes the students presently residing and needing accommodation
    """
    hostel = models.ForeignKey(
        to=swapper.get_model_name("kernel", "Residence"),
        on_delete=models.CASCADE,
        null=True
    )
    is_registered = models.BooleanField(default=True)
    residing_in_single = models.PositiveIntegerField(
        default=0,
    )
    residing_in_double = models.PositiveIntegerField(
        default=0,
    )
    residing_in_triple = models.PositiveIntegerField(
        default=0,
    )
    total_need_accommodation = models.PositiveIntegerField(
        default=0,
    )


    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        hostel = self.hostel
        total_need_accommodation = self.total_need_accommodation
        return f"{total_need_accommodation} students need accommodation in {hostel}"

