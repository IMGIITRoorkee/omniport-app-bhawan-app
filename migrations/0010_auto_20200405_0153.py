# Generated by Django 2.2.6 on 2020-04-04 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bhawan_app', '0009_visitor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaint',
            name='available_from',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='available_till',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='hostel',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='room_no',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='hostel',
        ),
        migrations.RemoveField(
            model_name='roombooking',
            name='booked_by_room_no',
        ),
        migrations.RemoveField(
            model_name='roombooking',
            name='forwarded',
        ),
        migrations.RemoveField(
            model_name='roombooking',
            name='hostel',
        ),
        migrations.AlterField(
            model_name='roombooking',
            name='status',
            field=models.CharField(choices=[('apr', 'Approved'), ('pen', 'Pending'), ('rej', 'Rejected'), ('fwd', 'Forwarded')], default='pen', max_length=10),
        ),
        migrations.CreateModel(
            name='ComplaintTimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('datetime_modified', models.DateTimeField(auto_now=True)),
                ('complaint_type', models.CharField(choices=[('ele', 'Electric'), ('toi', 'Toilet'), ('car', 'Carpentry'), ('cle', 'Cleaning'), ('oth', 'Other')], default='oth', max_length=10)),
                ('timing', models.ManyToManyField(to='bhawan_app.Timing')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
