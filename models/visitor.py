import swapper
from django.db import models

from formula_one.models.base import Model
from formula_one.utils.upload_to import UploadTo

from bhawan_app.models import RoomBooking


class Visitor(Model):
    """
    This model contains information about the visitor of a hostel room
    """

    person = models.ForeignKey(
        to=swapper.get_model_name('kernel', 'Person'),
        on_delete=models.CASCADE,
    )
    booking = models.ForeignKey(
        RoomBooking,
        on_delete=models.CASCADE,
        related_name='visitor',
    )
    relation = models.CharField(
        max_length=50,
    )
    photo_identification = models.FileField(
        upload_to=UploadTo('bhawan_app', 'visitor_id')
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        ResidentialInformation = swapper.load_model(
            'kernel',
            'ResidentialInformation',
        )
        full_name = self.person.full_name
        relation = self.relation
        booked_by = self.booking.resident
        booked_by_name = booked_by.person.full_name
        booked_by_room_no = booked_by.room_number
        return (
            f'{full_name} - {relation} of {booked_by_name} | '
            f'{booked_by_room_no}'
        )
