from django.contrib import admin
from .models import ParkingLot, Vehicle, ParkingSlot
# Register your models here.
admin.site.register(ParkingLot),
admin.site.register(ParkingSlot),
admin.site.register(Vehicle),   