# Generated by Django 5.1.7 on 2025-04-10 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0019_alter_user_otp_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverrequest',
            name='action_at',
            field=models.DateTimeField(null=True),
        ),
    ]
