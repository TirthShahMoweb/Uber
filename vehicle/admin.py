from django.contrib import admin

from .models import DocumentType, Vehicle, VehicleRequest

# Register your models here.

admin.site.register(Vehicle)
admin.site.register(VehicleRequest)
admin.site.register(DocumentType)
