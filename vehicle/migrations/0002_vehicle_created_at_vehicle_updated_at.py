# Generated by Django 5.1.7 on 2025-03-31 09:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
