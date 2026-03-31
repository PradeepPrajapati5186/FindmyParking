from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import ParkingLot, ParkingSlot, Vehicle
from .forms import ParkingLotForm, ParkingSlotForm, BulkSlotForm
from django.shortcuts import get_object_or_404, redirect
import qrcode
from io import BytesIO
from django.core.files import File
# Create your views here.
@login_required(login_url="login") #check in core.urls.py login name should exist..
def ownerDashboardView(request):
    return render(request, "Parkinglot/owner_dashboard.html")

@login_required(login_url="login")
def userDashboardView(request):
    return render(request, "Parkinglot/user_dashboard.html")

def parkingLotsView(request):
    lot = ParkingLot.objects.all()
    return render(request, "parking/parkinglots.html", {"lot": lot})


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

def parkingSlotsView(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id)
    slots = ParkingSlot.objects.filter(parking_lot=lot)
    return render(request, "parking/slots.html", {"slots": slots, "lot": lot})

def add_slot_view(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id)
    if request.method == "POST":
        form = ParkingSlotForm(request.POST)
        if form.is_valid():
            parking_slot = form.save(commit=False)
            parking_slot.parking_lot = lot
            parking_slot.save()
            return redirect('parking_slots', lot_id=lot.id)
    else:
        form = ParkingSlotForm()
    return render(request, "Parkinglot/add_slot.html", {"form": form, "lot": lot})

def bulk_add_slots(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id)

    if request.method == "POST":
        form = BulkSlotForm(request.POST)
        if form.is_valid():
            num = form.cleaned_data["number_of_slots"]

            # Extract defaults from form (model fields)
            slot_type = form.cleaned_data["slot_type"]
            length = form.cleaned_data["dimension_len"]
            width = form.cleaned_data["dimension_wid"]
            floor = form.cleaned_data["floor_level"]
            hr = form.cleaned_data["hourly_rate"]
            dr = form.cleaned_data["daily_rate"]
            mr = form.cleaned_data["monthly_rate"]

            # Find the current max slot number to continue sequentially
            existing_count = lot.slots.count()
            start_number = existing_count + 1

            for i in range(num):
                slot_number = f"{start_number + i}"  # sequential slot number

                slot = ParkingSlot.objects.create(
                    parking_lot=lot,
                    slot_number=slot_number,
                    slot_type=slot_type,
                    dimension_len=length,
                    dimension_wid=width,
                    floor_level=floor,
                    hourly_rate=hr,
                    daily_rate=dr,
                    monthly_rate=mr,
                    is_available=True,
                    is_reserved=False
                )

                # Generate QR code systematically
                qr_data = f"Lot-{lot.id}-Slot-{slot.slot_number}"
                qr = qrcode.make(qr_data)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                filename = f"lot{lot.id}_slot{slot.slot_number}.png"

                # Save QR code path into CharField
                slot.qr_code.save(filename , File(buffer),save  = True)
                slot.save()

            return redirect("parking/slots.html", lot_id=lot.id)
    else:
        form = BulkSlotForm()

    return render(request, "Parkinglot/bulk_add_slots.html", {"form": form, "lot": lot})

@login_required(login_url="login")
def delete_slot_view(request, slot_id):
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    lot_id = slot.parking_lot.id
    
    # Check if user is admin or owner of the parking lot
    if request.user.user_type in ['admin', 'owner']:
        slot.delete()
    
    return redirect('parking_slots', lot_id=lot_id)

@login_required(login_url="login")
def delete_lot_view(request, lot_id):
    lot = get_object_or_404(ParkingLot, id=lot_id)
    
    # Check if user is admin or owner of the parking lot
    if request.user.user_type in ['admin', 'owner'] :
        lot.delete()
    
    return redirect('parking_lots')
