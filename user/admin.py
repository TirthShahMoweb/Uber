from django.contrib import admin
from .models import User , Language, DriverRequest, Trip, TripFare, DocumentType, DocumentRequired ,DriverDetail, Role, Permission, RolePermission



# Register your models here.
admin.site.register(User)
admin.site.register(Language)
admin.site.register(DriverDetail)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(DocumentRequired)
admin.site.register(DocumentType)
admin.site.register(DriverRequest)
admin.site.register(Trip)
admin.site.register(TripFare)