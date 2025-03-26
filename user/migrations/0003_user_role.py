# Generated by Django 5.1.7 on 2025-03-24 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_permission_role_adminpermission'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.role'),
        ),
    ]