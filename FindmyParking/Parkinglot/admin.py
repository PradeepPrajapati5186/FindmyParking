from django.contrib import admin
from .models import ParkingLot, Vehicle, ParkingSlot,Reservation,Payment
# Register your models here.
admin.site.register(ParkingLot),
admin.site.register(ParkingSlot),
admin.site.register(Vehicle), 
admin.site.register(Reservation),    
admin.site.register(Payment),