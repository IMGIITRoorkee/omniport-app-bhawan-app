import swapper
from django.db import models
from django.core.validators import MaxValueValidator
from django.dispatch import receiver

from formula_one.models.base import Model
# from bhawan_app.utils.notification.push_notification import send_push_notification


class DefaultItem(Model):
    """
    Describes the name of the item replaced/repaired
    """

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        name = self.name
        return f"{name}"

