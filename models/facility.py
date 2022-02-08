from django.db import models
from django.dispatch import receiver

import swapper

from formula_one.models.base import Model
from formula_one.utils.upload_to import UploadTo

from bhawan_app.models import Timing
from bhawan_app.models.roles import HostelAdmin
from bhawan_app.models.resident import Resident
from bhawan_app.constants import facility_types
# from bhawan_app.utils.notification.push_notification import send_push_notification


class Facility(Model):
    """
    This model contains information about a facility of a hostel
    """

    hostel = models.ManyToManyField(
        to=swapper.get_model_name("kernel", "Residence"),
    )
    name = models.CharField(max_length=63, blank=False, null=False,)
    description = models.TextField(blank=True, null=True,)
    display_picture = models.ImageField(
        upload_to=UploadTo("bhawan_app", "hostel"),
        max_length=255,
        blank=True,
        null=True,
    )
    timings = models.ManyToManyField(Timing,)
    facility_type = models.CharField(
        max_length=10,
        choices=facility_types.FACILITY_TYPES,
        default=facility_types.OTHER,
    )

    def __str__(self):
        """
        Return the string representation of the model
        :return: the string representation of the model
        """

        name = self.name
        return f"{name}"

    class Meta:
        """
        Meta class for Facility
        """

        verbose_name_plural = "facilities"

@receiver(models.signals.post_save, sender=Facility)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        template = f"New facility started for your hostel : {instance.name} "
        all_residents = Resident.objects.filter(hostel=instance.hostel, is_resident=True)
        all_staff = HostelAdmin.objects.filter(hostel=instance.hostel)
        notify_residents = [resident.person.id for resident in all_residents]
        notify_staff = [staff.person.id for staff in all_staff]
        notify_users = list(set(notify_residents + notify_staff))
        # send_push_notification(template, True, notify_users)
