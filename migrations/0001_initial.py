# Generated by Django 2.2.3 on 2020-11-08 14:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import formula_one.utils.upload_to


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.KERNEL_PERSON_MODEL),
        migrations.swappable_dependency(settings.KERNEL_RESIDENCE_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Resident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('room_number', models.CharField(max_length=10)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.KERNEL_RESIDENCE_MODEL)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_PERSON_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RoomBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('apr', 'Approved'), ('pen', 'Pending'), ('rej', 'Rejected'), ('fwd', 'Forwarded'), ('cnf', 'Confirmed')], default='pen', max_length=10)),
                ('requested_from', models.DateField()),
                ('requested_till', models.DateField()),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bhawan_app.Resident')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Timing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('day', models.CharField(choices=[('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday'), ('dai', 'Daily')], max_length=50)),
                ('start', models.TimeField()),
                ('end', models.TimeField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=63, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('relation', models.CharField(max_length=50)),
                ('photo_identification', models.FileField(upload_to=formula_one.utils.upload_to.UploadTo('bhawan_app', 'visitor_id'))),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitor', to='bhawan_app.RoomBooking')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_PERSON_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('display_picture', models.ImageField(upload_to=formula_one.utils.upload_to.UploadTo('bhawan_app', 'hostel'))),
                ('homepage_url', models.URLField(blank=True, verbose_name='Homepage URL')),
                ('hostel', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_RESIDENCE_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=63)),
                ('description', models.TextField(blank=True, null=True)),
                ('display_picture', models.ImageField(blank=True, max_length=255, null=True, upload_to=formula_one.utils.upload_to.UploadTo('bhawan_app', 'hostel'))),
                ('facility_type', models.CharField(choices=[('mes', 'Mess'), ('spo', 'Sports'), ('can', 'Canteen'), ('lau', 'Laundry'), ('oth', 'Other')], default='oth', max_length=10)),
                ('hostel', models.ManyToManyField(to=settings.KERNEL_RESIDENCE_MODEL)),
                ('timings', models.ManyToManyField(to='bhawan_app.Timing')),
            ],
            options={
                'verbose_name_plural': 'facilities',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=63)),
                ('description', models.TextField(blank=True, null=True)),
                ('display_picture', models.ImageField(blank=True, max_length=255, null=True, upload_to=formula_one.utils.upload_to.UploadTo('bhawan_app', 'hostel'))),
                ('date', models.DateField()),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_RESIDENCE_MODEL)),
                ('timings', models.ManyToManyField(to='bhawan_app.Timing')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('designation', models.CharField(choices=[('aw', 'Assistant warden'), ('cw', 'Chief warden'), ('sup', 'Supervisor'), ('war', 'Warden'), ('waw', 'Warden wellness'), ('bscy', 'Bhawan secretary'), ('cscy', 'Cultural secretary'), ('mscy', 'Maintenance secretary'), ('mescy', 'Mess secretary'), ('sscy', 'Sports secretary'), ('tscy', 'Technical secretary')], max_length=5, unique=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_PERSON_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('complaint_type', models.CharField(choices=[('ele', 'Electric'), ('toi', 'Toilet'), ('car', 'Carpentry'), ('cle', 'Cleaning'), ('mes', 'Mess'), ('oth', 'Other')], default='oth', max_length=10)),
                ('status', models.CharField(choices=[('res', 'Resolved'), ('pen', 'Pending'), ('unr', 'Unresolved')], default='pen', max_length=10)),
                ('description', models.TextField()),
                ('failed_attempts', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(3)])),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bhawan_app.Resident')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HostelAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('designation', models.CharField(choices=[('aw', 'Assistant warden'), ('cw', 'Chief warden'), ('sup', 'Supervisor'), ('war', 'Warden'), ('waw', 'Warden wellness'), ('bscy', 'Bhawan secretary'), ('cscy', 'Cultural secretary'), ('mscy', 'Maintenance secretary'), ('mescy', 'Mess secretary'), ('sscy', 'Sports secretary'), ('tscy', 'Technical secretary')], max_length=5)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_RESIDENCE_MODEL)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_PERSON_MODEL)),
            ],
            options={
                'unique_together': {('hostel', 'designation'), ('person', 'hostel')},
            },
        ),
        migrations.CreateModel(
            name='ComplaintTimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('complaint_type', models.CharField(choices=[('ele', 'Electric'), ('toi', 'Toilet'), ('car', 'Carpentry'), ('cle', 'Cleaning'), ('mes', 'Mess'), ('oth', 'Other')], default='oth', max_length=10)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.KERNEL_RESIDENCE_MODEL)),
                ('timing', models.ManyToManyField(to='bhawan_app.Timing')),
            ],
            options={
                'unique_together': {('complaint_type', 'hostel')},
            },
        ),
    ]
