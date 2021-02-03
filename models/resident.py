import swapper
from django.db import models
from django.core.exceptions import ValidationError

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
    father = models.OneToOneField(
        to=swapper.get_model_name("Kernel", "Person"), on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='residents_father'
    )
    fathers_contact = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )
    mother = models.OneToOneField(
        to=swapper.get_model_name("Kernel", "Person"), on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='residents_mother'
    )
    mothers_contact = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    def clean(self):
        """
        A resident of any Bhawan must be Student
        """

        Student = swapper.load_model('Kernel', 'Student')
        is_student = Student.objects.filter(person=self.person).exists()
        if not is_student:
            raise ValidationError(
                    f"{self.person.full_name} is not a student"
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

        room_no = self.room_number
        hostel = self.hostel.name
        person = self.person
        return f"{person} - {hostel}({room_no})"
