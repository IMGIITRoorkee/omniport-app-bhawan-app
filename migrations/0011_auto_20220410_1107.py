# Generated by Django 3.2.8 on 2022-04-10 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bhawan_app', '0010_auto_20220330_2032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='designation',
            field=models.CharField(choices=[('aw', 'Assistant warden'), ('aw2', 'Assistant warden 2'), ('aw3', 'Assistant warden 3'), ('cw', 'Chief warden'), ('msw', 'Mess Warden'), ('sup', 'Supervisor'), ('war', 'Warden'), ('waw', 'Warden wellness'), ('bscy', 'Bhawan secretary'), ('cscy', 'Cultural secretary'), ('mscy', 'Maintenance secretary'), ('mescy', 'Mess secretary'), ('sscy', 'Sports secretary'), ('tscy', 'Technical secretary'), ('dosw', 'DEAN of students welfare'), ('gsha', 'GENSEC Hostel Afairs')], max_length=5, unique=True),
        ),
        migrations.AlterField(
            model_name='hosteladmin',
            name='designation',
            field=models.CharField(choices=[('aw', 'Assistant warden'), ('aw2', 'Assistant warden 2'), ('aw3', 'Assistant warden 3'), ('cw', 'Chief warden'), ('msw', 'Mess Warden'), ('sup', 'Supervisor'), ('war', 'Warden'), ('waw', 'Warden wellness'), ('bscy', 'Bhawan secretary'), ('cscy', 'Cultural secretary'), ('mscy', 'Maintenance secretary'), ('mescy', 'Mess secretary'), ('sscy', 'Sports secretary'), ('tscy', 'Technical secretary'), ('dosw', 'DEAN of students welfare'), ('gsha', 'GENSEC Hostel Afairs')], max_length=5),
        ),
        migrations.AlterField(
            model_name='resident',
            name='fee_type',
            field=models.CharField(choices=[('liv', 'LIVING'), ('nlv', 'NOT LIVING'), ('nd', 'NON DINING'), ('inl', 'INTERNATIONAL STUDENT')], default='liv', max_length=10),
        ),
    ]
