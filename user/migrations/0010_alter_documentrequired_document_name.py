# Generated by Django 5.1.7 on 2025-04-01 09:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_documenttype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentrequired',
            name='document_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='documents', to='user.documenttype'),
        ),
    ]
