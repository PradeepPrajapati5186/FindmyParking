from django.db import models
from core.models import User

VEHICLE_TYPES = [
    ('car', 'Car'),
    ('bike', 'Bike'),
    ('truck', 'Truck'),
    ('suv', 'SUV'),
]

class ParkingLot(models.Model):
    lot_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    total_slots = models.IntegerField()
    available_slots = models.IntegerField(default=0)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_operational = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lots_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parkinglot_image = models.ImageField(upload_to='Parkinglot_images/', null=True, blank=True)

    def __str__(self):
        return self.lot_name

class ParkingSlot(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="slots")
    slot_number = models.CharField(max_length=10)
    floor_level = models.IntegerField(default=0)
    slot_type = models.CharField(max_length=20, choices=[
        ('regular', 'Regular'),
        ('ev', 'EV'),
        ('handicap', 'Handicap'),
        ('vip', 'VIP'),
    ])
    is_available = models.BooleanField(default=True)
    is_reserved = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    dimension_len = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dimension_wid = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parking_lot.lot_name} - {self.slot_number}"

class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=[
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('ev', 'EV'),
        ('suv', 'SUV'),
    ])
    vehicle_model = models.CharField(max_length=50, null=True, blank=True)
    vehicle_color = models.CharField(max_length=20, null=True, blank=True)
    is_electric = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vehicle_number

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name="reservations")
    vehicle_number = models.CharField(max_length=20, blank=True, default='')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='car')
    reservation_type = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.DurationField()
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    booking_reference = models.CharField(max_length=20, unique=True)
    qr_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_extended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation {self.booking_reference} - {self.user}"

class Payment(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
    ])
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ])
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_gateway = models.CharField(max_length=50, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    refund_date = models.DateTimeField(null=True, blank=True)
    receipt_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.user}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=[
        ('reservation', 'Reservation'),
        ('payment', 'Payment'),
        ('alert', 'Alert'),
        ('reminder', 'Reminder'),
    ])
    title = models.CharField(max_length=100)
    message = models.TextField()
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, default='normal', choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ])
    sent_via = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('in_app', 'In-App'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review {self.rating} by {self.user}"

