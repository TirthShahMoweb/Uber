# Generated by Django 5.1.7 on 2025-04-29 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0028_rename_tripfares_tripfare'),
        ('vehicle', '0011_alter_vehicle_vehicle_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='vehicle_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vehicle.vehicle'),
        ),
    ]
