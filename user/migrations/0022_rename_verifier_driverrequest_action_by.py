# Generated by Django 5.1.7 on 2025-04-15 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_alter_driverrequest_action_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='driverrequest',
            old_name='verifier',
            new_name='action_by',
        ),
    ]
