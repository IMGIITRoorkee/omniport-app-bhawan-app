from django.db import models
from django.contrib.contenttypes import fields as contenttypes_fields

import swapper
from formula_one.models.base import Model
from bhawan_app.models.hostel_visitor import HostelVisitor

class HostelRoomBooking(Model):
    """
    This model holds guest room booking information of a hostel
    """

    hostel = models.ForeignKey(
        to=swapper.get_model_name('kernel', 'Residence'),
        on_delete=models.CASCADE,
    )
    person = models.ForeignKey(
        to=swapper.get_model_name('kernel', 'Person'),
        on_delete=models.CASCADE,
    )
    time_of_booking = models.DateTimeField(
        auto_now_add=True,
    )
    from_date = models.DateTimeField()

    to_date = models.DateTimeField()

    number_of_rooms = models.PositiveIntegerField()
    
    visitor_details = models.ManyToManyField(HostelVisitor)

    booking_status = models.CharField(
        max_length=255,
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        hostel = self.hostel
        person = self.person
        return f'{hostel}:{person}'

    class Meta:
        """
        Meta class for HostelRoomBooking
        """

        ordering = ['-time_of_booking']
        verbose_name_plural = 'hostel room booking'

