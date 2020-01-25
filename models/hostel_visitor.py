from django.db import models
from django.contrib.contenttypes import fields as contenttypes_fields

import swapper
from formula_one.models.base import Model

class HostelVisitor(Model):
    """
    This model holds information of guest room visitors of a hostel
    """

    visitor_name = models.CharField(
        max_length=255,
    )
    visitor_relation = models.CharField(
        max_length=255,
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        visitor_name = self.visitor_name
        visitor_relation = self.visitor_relation
        return f'{visitor_name}:{visitor_relation}'

    class Meta:
        """
        Meta class for hostel visitor
        """

        verbose_name_plural = 'hostel visitor'
        