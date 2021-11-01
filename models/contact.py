from django.db import models
from django.contrib.contenttypes import fields as contenttypes_fields

import swapper
from formula_one.models.base import Model
from bhawan_app.constants import designations


class Contact(Model):
    """
    This model holds contact information of the staff concerned with a hostel
    """

    person = models.ForeignKey(
        to=swapper.get_model_name("kernel", "Person"), on_delete=models.CASCADE,
    )
    hostel = models.ForeignKey(
        to=swapper.get_model_name("kernel", "Residence"),
        on_delete=models.CASCADE,
    )
    designation = models.CharField(
        max_length=5, unique=True, choices=designations.DESIGNATIONS,
    )
    contact_information = contenttypes_fields.GenericRelation(
        to="formula_one.ContactInformation",
        related_query_name="hostel_contact",
        content_type_field="entity_content_type",
        object_id_field="entity_object_id",
    )

    @property
    def designation_name(self):
        """
        Return the name of the designation
        :return: the name of the designation
        """

        return self.get_designation_display()

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        hostel = self.hostel
        person = self.person
        designation = self.designation_name
        return f"{hostel}: {person}, {designation}"
