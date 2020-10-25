from django.db import models

import swapper

from formula_one.models.base import Model
from formula_one.utils.upload_to import UploadTo

from bhawan_app.models import Timing
from bhawan_app.constants import facility_types


class Facility(Model):
    """
    This model contains information about a facility of a hostel
    """

    hostel = models.ManyToManyField(
        to=swapper.get_model_name("kernel", "Residence"),
    )
    name = models.CharField(max_length=63, blank=False, null=False,)
    description = models.TextField(blank=True, null=True,)
    display_picture = models.ImageField(
        upload_to=UploadTo("bhawan_app", "hostel"),
        max_length=255,
        blank=True,
        null=True,
    )
    timings = models.ManyToManyField(Timing,)
    facility_type = models.CharField(
        max_length=10,
        choices=facility_types.FACILITY_TYPES,
        default=facility_types.OTHER,
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        name = self.name
        return f"{name}"

    class Meta:
        """
        Meta class for Facility
        """

        verbose_name_plural = "facilities"
