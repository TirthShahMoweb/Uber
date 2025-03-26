from django.db import models
import os, uuid

from utils.baseModel import BaseModel



def unique_vehicle_images_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # e.g., .jpg or .png
    unique_filename = f"{uuid.uuid4()}{ext}"
    # Return the full upload path
    return os.path.join("vehicle_images/", unique_filename)

class WheelerChoices(models.TextChoices):
    TWO_WHEELER = '2', '2 Wheeler'
    THREE_WHEELER = '3', '3 Wheeler'
    FOUR_WHEELER = '4', '4 Wheeler'


class VerificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    REJECTED = 'rejected', 'Rejected'
    APPROVED = 'approved', 'Approved'


class Vehicle(BaseModel):

    driver = models.ForeignKey('user.DriverDetail', on_delete=models.CASCADE)
    vehicle_image = models.ImageField(upload_to=unique_vehicle_images_path, null=False)
    vehicle_rc = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=WheelerChoices)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    status = models.CharField(max_length=10, choices=VerificationStatus, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)