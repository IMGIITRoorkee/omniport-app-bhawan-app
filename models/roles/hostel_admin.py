import swapper
from django.db import models
from django.core.exceptions import ValidationError
from formula_one.models.base import Model

from bhawan_app.models.resident import Resident

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
        null=True,
        blank=True,
    )

    def clean(self):
        """
        If the designation is a Student Council,
        The person must be a resident of the hostel
        """
        if(self.designation in designations.STUDENT_COUNCIL_LIST):
            try:
                resident = Resident.objects.get(person=self.person, is_resident = True)
                if(resident.hostel != self.hostel):
                    raise ValidationError(
                        f"{self.person.full_name} is not a resident of {self.hostel.code}"
                    )
            except Resident.DoesNotExist:
                raise ValidationError(
                    f"{self.person.full_name} is not a resident of {self.hostel.code}"
                )

    def save(self, *args, **kwargs):
        """
        Override save method to check the custom validations written in clean
        method
        """

        # Intrinsically calls the `clean` method
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        person = self.person
        designation = self.get_designation_display()
        if(self.hostel):
            hostel = self.hostel.name
        else:
            hostel = "GLOBAL"
        return f"{person} - {designation}, {hostel}"

    class Meta:
        """"
        There can't be two instances of this model with
            1. Same hostel and designation.
            2. Same person and hostel.
        """
        unique_together = (('hostel', 'designation'), ('person', 'hostel'))
