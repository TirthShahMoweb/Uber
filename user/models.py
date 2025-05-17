from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

from utils.baseModel import BaseModel
from Uber import settings
import uuid, os



def unique_profile_pic_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # e.g., .jpg or .png
    unique_filename = f"{uuid.uuid4()}{ext}"
    # Return the full upload path
    return os.path.join("profile_pics/", unique_filename)


class GenderChoices(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'


class UserTypeChoices(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    DRIVER = 'driver', 'Driver'
    ADMIN = 'admin', 'Admin'


class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(unique=True, null = True, blank= True, default=None)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=128)
    mobile_number = models.CharField(max_length=15, unique=True)
    profile_pic = models.ImageField(upload_to=unique_profile_pic_path , blank=True, null=True)
    thumbnail_pic = models.ImageField(upload_to='thumbnail_pics/', blank=True, null=True)
    otp = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    otp_created_at = models.TimeField(null=True, blank=True)
    verification_code = models.CharField(max_length=128 , null=True, blank=True)
    verification_code_created_at = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices = GenderChoices, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices = UserTypeChoices, default='customer')
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)


    USERNAME_FIELD = 'mobile_number'


class Language(BaseModel):

    name = models.CharField(unique=True,max_length=100)


def unique_aadhar_photos_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # e.g., .jpg or .png
    unique_filename = f"{uuid.uuid4()}{ext}"
    # Return the full upload path
    return os.path.join("aadhar_photos/", unique_filename)


class VerificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    REJECTED = 'rejected', 'Rejected'
    APPROVED = 'approved', 'Approved'


class DriverDetail(BaseModel):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dob = models.DateField()
    lang = models.ManyToManyField(Language, related_name="driver_details_lang")
    in_use = models.ForeignKey('vehicle.Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    amount_remaining = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    verified_at = models.DateTimeField(null = True)
    verification_documents = models.ManyToManyField('DocumentRequired', related_name='driver_detail_documents')
    is_online = models.BooleanField(default=False)
    last_online_at = models.DateTimeField(null=True, blank=True)


class DriverRequest(BaseModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_request_user")
    action_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_request_verifier", null=True, blank=True)
    dob = models.DateField()
    lang = models.ManyToManyField(Language, related_name="driver_request_lang")
    status = models.CharField(max_length=10, choices=VerificationStatus, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)
    action_at = models.DateTimeField(null = True, blank=True)
    verification_documents = models.ManyToManyField('DocumentRequired', related_name='driver_request_documents')


class DocumentRequired(BaseModel):
    document_name = models.ForeignKey('DocumentType', on_delete=models.PROTECT, related_name='documents')
    document_text = models.TextField(null=True, blank=True)
    document_image = models.ImageField(upload_to=unique_aadhar_photos_path, null=True, blank=True)


class DocumentFieldType(models.TextChoices):
    IMAGE = 'image', 'Image'
    TEXT = 'text', 'Text'


class DocumentType(BaseModel):
    document_key = models.CharField(max_length=50)
    document_label = models.CharField(max_length=255)
    is_required = models.BooleanField(default=True)
    field_type = models.CharField(max_length=20, choices=DocumentFieldType)


class Role(BaseModel):
    role_name = models.CharField(max_length=50)
    description = models.TextField()


class Permission(BaseModel):
    permission_name = models.CharField(max_length=50)
    description = models.TextField()


class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission ,related_name="permissions")


class CancelByStatus(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    DRIVER = 'driver', 'Driver'
    AUTO = 'auto', 'Auto'

class TripStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    ON_GOING = 'on_going', 'On Going'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class WheelerChoices(models.TextChoices):
    TWO_WHEELER = '2 Wheeler', '2 Wheeler'
    THREE_WHEELER = '3 Wheeler', '3 Wheeler'
    FOUR_WHEELER = '4 Wheeler', '4 Wheeler'


class Trip(BaseModel):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer")
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver", null=True, blank=True)
    vehicle_id = models.ForeignKey('vehicle.Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_type = models.CharField(max_length=10, choices=WheelerChoices, null=True, blank=True)
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    pickup_time = models.DateTimeField(null=True, blank=True)
    drop_time = models.DateTimeField(null=True, blank=True)
    drop_location_latitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)
    drop_location_longitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)
    pickup_location_latitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)
    pickup_location_longitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.DecimalField(max_digits=10, decimal_places=2)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TripStatus, default='pending')
    description = models.TextField(null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    cancelled_by = models.CharField(max_length=20, choices=CancelByStatus, null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)


class TripFare(BaseModel):
    vehicle_type = models.CharField(max_length=50)
    normal_fare = models.DecimalField(max_digits=10, decimal_places=2)
    night_time_fare = models.DecimalField(max_digits=10, decimal_places=2)
    peak_time_fare = models.DecimalField(max_digits=10, decimal_places=2)
    night_time_starting = models.TimeField()
    night_time_ending = models.TimeField()
    peak_time_morning_starting = models.TimeField()
    peak_time_morning_ending = models.TimeField()
    peak_time_evening_starting = models.TimeField()
    peak_time_evening_ending = models.TimeField()


class TripLocation(BaseModel):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="locations")
    latitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=19, decimal_places=16, null=True, blank=True)