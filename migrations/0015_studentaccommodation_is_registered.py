# Generated by Django 3.2 on 2022-06-07 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bhawan_app', '0014_alter_resident_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentaccommodation',
            name='is_registered',
            field=models.BooleanField(default=True),
        ),
    ]
