# Generated by Django 5.1.7 on 2025-04-01 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_alter_documentrequired_document_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentrequired',
            name='document_name',
            field=models.CharField(max_length=255),
        ),
    ]
