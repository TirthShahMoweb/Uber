from django.contrib import admin

from .models import Vehicle, VehicleRequest, DocumentType
# Register your models here.

admin.site.register(Vehicle)
admin.site.register(VehicleRequest)
admin.site.register(DocumentType)