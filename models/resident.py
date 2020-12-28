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
    having_computer = models.BooleanField(default=True)
    father = models.OneToOneField(
        to=swapper.get_model_name("Kernel", "Person"), on_delete=models.CASCADE,
        null=True,
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
        related_name='residents_mother'
    )
    mothers_contact = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        """
        A resident of any Bhawan must be Student
        """
        try:
            Student = swapper.load_model('Kernel', 'Student')
            student=Student.objects.get(person=self.person)
            super().save(*args, **kwargs)
        except Student.DoesNotExist:
            raise ValueError(
                    f"{self.person.full_name} is not a student"
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
