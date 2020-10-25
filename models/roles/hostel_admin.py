import swapper
from django.db import models
from formula_one.models.base import Model

from bhawan_app.constants import designations


class HostelAdmin(Model):
    """
    This model holds information pertaining to the administrator of a hostel
    """
    person = models.ForeignKey(
        to=swapper.get_model_name('kernel', 'Person'),
        on_delete=models.CASCADE,
    )
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
        """"
        There can't be two instances of this model with 
            1. Same hostel and designation.
            2. Same person and hostel.
        """
        unique_together = (('hostel', 'designation'), ('person', 'hostel'))
