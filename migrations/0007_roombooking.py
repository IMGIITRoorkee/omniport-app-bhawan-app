# Generated by Django 2.2.6 on 2020-02-02 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.KERNEL_PERSON_MODEL),
        migrations.swappable_dependency(settings.KERNEL_RESIDENCE_MODEL),
        ("bhawan_app", "0006_facility"),
    ]

    operations = [
        migrations.CreateModel(
            name="RoomBooking",
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('apr', 'Approved'), ('pen', 'Pending'), ('rej', 'Rejected')], default='pen', max_length=10)),
                ('requested_from', models.DateField()),
                ('requested_till', models.DateField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_PERSON_MODEL)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_RESIDENCE_MODEL)),
                ('forwarded', models.BooleanField(default=False)),
                ('booked_by_room_no', models.PositiveIntegerField()),
                
            ],
            options={"abstract": False,},
        ),
    ]
