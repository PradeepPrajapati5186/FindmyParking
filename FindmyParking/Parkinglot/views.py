import math
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.utils import timezone
from .models import ParkingLot, ParkingSlot, Reservation, Payment
from .forms import ParkingLotForm, ParkingSlotForm, BulkSlotForm, ReservationForm
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils.crypto import get_random_string
# Create your views here.
@login_required(login_url="login") #check in core.urls.py login name should exist..
def adminDashboardView(request):
    return render(request, "Parkinglot/owner_dashboard.html")

@login_required(login_url="login")
def userDashboardView(request):
    return render(request, "Parkinglot/user_dashboard.html")

def release_expired_slots():
    """Utility to free up slots whose active reservations have expired."""
    now = timezone.now()
    expired_reservations = Reservation.objects.filter(
        end_time__lt=now,
        status__in=['active', 'confirmed']
    )
    for res in expired_reservations:
        res.status = 'completed'
        res.save(update_fields=['status'])
        
        slot = res.parking_slot
        slot.is_available = True
        slot.save(update_fields=['is_available'])

def parkingLotsView(request):
    release_expired_slots()
    query = request.GET.get('q', '').strip()
    if query:
        lots = ParkingLot.objects.filter(
            Q(lot_name__icontains=query) | Q(city__icontains=query)
        )
    else:
        lots = ParkingLot.objects.all()

    # Calculate available slots dynamically for each lot
    for lot in lots:
        lot.available_slots = lot.get_available_slots_count()

    # Paginate results (6 lots per page)
    paginator = Paginator(lots, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "parking/parkinglots.html", {
        "page_obj": page_obj,
        "query": query
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

def parkingSlotsView(request, lot_id):
    release_expired_slots()
    lot = get_object_or_404(ParkingLot, id=lot_id)
    # Order slots numerically by slot_number, with available slots first
    slots = ParkingSlot.objects.filter(parking_lot=lot).annotate(
        slot_num=Cast('slot_number', IntegerField())
    ).order_by('-is_available', 'slot_num')

    # Paginate results (10 slots per page)
    paginator = Paginator(slots, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "parking/slots.html", {
        "page_obj": page_obj,
        "lot": lot
    })

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

@login_required(login_url="login")
def start_reservation(request, slot_id):
    # Direct to reservation form with slot pre-filled
    return redirect('create_reservation', slot_id=slot_id)

@login_required(login_url="login")
def create_reservation(request, slot_id):
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.parking_slot = slot
            reservation.booking_reference = get_random_string(10).upper()
            reservation.duration = reservation.end_time - reservation.start_time
            reservation.status = 'pending'

            # Calculate total_amount based on reservation_type
            if reservation.reservation_type == 'hourly':
                hours = reservation.duration.total_seconds() / 3600
                rounded_hours = math.ceil(hours)  # round up to next full hour
                reservation.total_amount = rounded_hours * slot.hourly_rate  # hourly rate ₹100

            elif reservation.reservation_type == 'daily':
                reservation.total_amount = slot.daily_rate
            else:
                reservation.total_amount = slot.monthly_rate

            reservation.save()
            
            # Mark slot as unavailable when reservation is created
            slot.is_available = False
            slot.save()
            
            return redirect('reservation_success', reservation_id=reservation.id)
    else:
        form = ReservationForm()

    return render(request, 'reservation/reservation.html', {'form': form, 'slot': slot})


def reservation_success(request, reservation_id):

    reservation = Reservation.objects.get(id=reservation_id)
    return render(request, 'reservation/reservation_success.html', {'reservation': reservation})

def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    # mark as cancelled
    reservation.status = "cancelled"
    reservation.save()
    
    # Mark the associated slot as available again
    slot = reservation.parking_slot
    slot.is_available = True
    slot.save()
    
    return render(request, "reservation/cancel_success.html", {"reservation": reservation})

def pay_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Initialize razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    payment_amount = int(reservation.total_amount * 100)
    
    # Create order
    razorpay_order = client.order.create({
        "amount": payment_amount,
        "currency": "INR",
        "receipt": f"receipt_{reservation.id}",
        "payment_capture": "1"
    })
    
    Payment.objects.create(
        reservation=reservation,
        user=request.user,
        amount=reservation.total_amount,
        payment_method='',
        payment_status='pending',
        transaction_id=razorpay_order['id'],
        payment_gateway='razorpay'
    )
    
    context = {
        "reservation": reservation,
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_merchant_key": settings.RAZORPAY_KEY_ID,
        "razorpay_amount": payment_amount,
        "currency": "INR",
    }
    return render(request, "reservation/pay_reservation.html", context)

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(transaction_id=razorpay_order_id)
            payment.payment_status = 'completed'
            payment.save()
            
            reservation = payment.reservation
            reservation.status = 'active'
            reservation.save()

            return render(request, "reservation/payment_success.html", {"reservation": reservation})
        except razorpay.errors.SignatureVerificationError:
            return render(request, "reservation/payment_failed.html", {})
    return redirect("parking_lots")
