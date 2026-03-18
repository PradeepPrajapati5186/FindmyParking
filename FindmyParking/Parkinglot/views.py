from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import ParkingLot, ParkingSlot, Vehicle
from .forms import ParkingLotForm
# Create your views here.
@login_required(login_url="login") #check in core.urls.py login name should exist..
def ownerDashboardView(request):
    return render(request, "Parkinglot/owner_dashboard.html")

@login_required(login_url="login")
def userDashboardView(request):
    return render(request, "Parkinglot/user_dashboard.html")

def parkingLotsView(request):
    lots = ParkingLot.objects.all()
    operational_slots= lots.filter(is_operational=True).aggregate(total_slots=models.Sum('total_slots'), available_slots= models.Sum('available_slots'))
    return render(request, "Parkinglot/parkinglot.html",{
         "lots": lots, 
         "operational_slots": operational_slots, 
         "total_slots": operational_slots['total_slots'] or 0,
        "available_slots": operational_slots['available_slots'] or 0
         })

def parkingLotFormView(request):
    if request.method == "POST":
        form = ParkingLotForm(request.POST, request.FILES)
        if form.is_valid():
            parking_lot = form.save(commit=False)
            parking_lot.created_by = request.user
            parking_lot.save()
            return render(request, "Parkinglot/owner_dashboard.html")
    else:
        form = ParkingLotForm()
    return render(request, "Parkinglot/parkinglot_form.html", {"form": form})