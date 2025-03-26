# Generated by Django 5.1.7 on 2025-03-24 16:56

import django.db.models.deletion
import django.utils.timezone
import user.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_user_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentRequired',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('document_name', models.CharField(max_length=255)),
                ('document_text', models.TextField(blank=True, null=True)),
                ('document_image', models.ImageField(blank=True, null=True, upload_to=user.models.unique_aadhar_photos_path)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DriverDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('dob', models.DateField()),
                ('amount_remaining', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount_received', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('verified_at', models.DateTimeField(null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('rejected', 'Rejected'), ('approved', 'Approved')], default='pending', max_length=10)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('lang', models.ManyToManyField(related_name='drivers', to='user.language')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
