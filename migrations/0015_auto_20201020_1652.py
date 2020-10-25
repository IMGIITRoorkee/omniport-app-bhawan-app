# Generated by Django 2.2.3 on 2020-10-20 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.KERNEL_PERSON_MODEL),
        migrations.swappable_dependency(settings.KERNEL_RESIDENCE_MODEL),
        ('bhawan_app', '0014_auto_20200428_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hosteladmin',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_PERSON_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='hosteladmin',
            unique_together={('person', 'hostel'), ('hostel', 'designation')},
        ),
        migrations.RemoveField(
            model_name='hosteladmin',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='hosteladmin',
            name='start_date',
        ),
    ]
