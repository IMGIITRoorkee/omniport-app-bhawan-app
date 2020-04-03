# Generated by Django 2.2.6 on 2020-02-14 07:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import formula_one.utils.upload_to


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.KERNEL_PERSON_MODEL),
        ('bhawan_app', '0008_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('relation', models.CharField(max_length=50)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitor', to='bhawan_app.RoomBooking')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_PERSON_MODEL)),
                ('photo_identification', models.FileField(upload_to=formula_one.utils.upload_to.UploadTo('bhawan_app', 'visitor_id'))),
            ],
            options={"abstract": False,},
        ),
    ]
