# Generated by Django 5.1.7 on 2025-04-15 06:27

import vehicle.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0004_vehiclerequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_back_image',
            field=models.ImageField(upload_to=vehicle.models.unique_vehicle_images_path),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_front_image',
            field=models.ImageField(upload_to=vehicle.models.unique_vehicle_images_path),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_leftSide_image',
            field=models.ImageField(upload_to=vehicle.models.unique_vehicle_images_path),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_number',
            field=models.CharField(max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_rc_back',
            field=models.ImageField(upload_to=vehicle.models.unique_vehicle_rcimage_path),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_rc_front',
            field=models.ImageField(upload_to=vehicle.models.unique_vehicle_rcimage_path),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_rightSide_image',
            field=models.ImageField(upload_to=vehicle.models.unique_vehicle_images_path),
        ),
    ]
