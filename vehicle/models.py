from django.db import models
import os, uuid

from utils.baseModel import BaseModel



def unique_vehicle_images_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # e.g., .jpg or .png
    unique_filename = f"{uuid.uuid4()}{ext}"
    # Return the full upload path
    return os.path.join("vehicle_images/", unique_filename)

def unique_vehicle_rcimage_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # e.g., .jpg or .png
    unique_filename = f"{uuid.uuid4()}{ext}"
    # Return the full upload path
    return os.path.join("vehicle_rc/", unique_filename)

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
    vehicle_number = models.CharField(max_length=8, unique=True)
    vehicle_chassis_number = models.CharField(max_length=17, unique=True,null=True)
    vehicle_engine_number = models.CharField(max_length=17, unique=True,null=True)
    vehicle_type = models.CharField(max_length=10, choices=WheelerChoices)
    verified_at = models.DateTimeField(null = True)
    verification_documents = models.ManyToManyField('DocumentType', related_name='vehicle_approve_documents')


class VehicleRequest(BaseModel):
    driver = models.ForeignKey('user.DriverDetail', on_delete=models.CASCADE)
    action_by = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="vehicle_request_verifier", null=True, blank=True)
    vehicle_number = models.CharField(max_length=8, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=WheelerChoices)
    status = models.CharField(max_length=10, choices=VerificationStatus, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)
    action_at = models.DateTimeField(null=True, blank=True)
    verification_documents = models.ManyToManyField('DocumentType', related_name='vehicle_request_documents')


class DocumentType(BaseModel):
    document_type = models.CharField(max_length=100, unique=True) # vehicle_front_image, vehicle_back_image, vehicle_leftSide_image, vehicle_rightSide_image, vehicle_rc_front_image, vehicle_rc_back_image
    document_image = models.ImageField(upload_to=unique_vehicle_images_path, null=True, blank=True)
    document_name = models.CharField(max_length=100, null=True, blank=True)
    document_size = models.IntegerField(null=True, blank=True)
    document_mime_type = models.CharField(max_length=100, null=True, blank=True)