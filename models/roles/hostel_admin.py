import swapper
from django.db import models

from kernel.models.roles.base import AbstractRole

from bhawan_app.constants import designations


class HostelAdmin(AbstractRole):
    """
    This model holds information pertaining to the administrator of a hostel
    """

    designation = models.CharField(max_length=5, choices=designations.DESIGNATIONS,)
    hostel = models.ForeignKey(
        to=swapper.get_model_name("kernel", "Residence"), on_delete=models.CASCADE,
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        person = self.person
        designation = self.get_designation_display()
        hostel = self.hostel.name
        return f"{person} - {designation}, {hostel}"
    
    class Meta:
        unique_together = ('hostel', 'designation')
