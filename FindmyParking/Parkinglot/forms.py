from django import forms
from django.core.validators import RegexValidator
from .models import ParkingLot, ParkingSlot, Reservation, VEHICLE_TYPES

VEHICLE_NUMBER_REGEX = RegexValidator(
    regex=r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$',
    message='Enter a valid vehicle number (e.g., GJ01AB1234).'
)

class ParkingLotForm(forms.ModelForm):
    class Meta:
        model = ParkingLot
        fields = ['lot_name', 'address', 'city', 'state', 'zipcode',
                  'latitude', 'longitude', 'total_slots', 'available_slots',
                  'opening_time', 'closing_time', 'is_operational', 'parkinglot_image']
        widgets = {
            'lot_name':       forms.TextInput(attrs={'class': 'lf-input', 'placeholder': 'e.g. Central Mall Parking'}),
            'address':        forms.Textarea(attrs={'class': 'lf-input', 'rows': 3, 'placeholder': 'Full street address'}),
            'city':           forms.TextInput(attrs={'class': 'lf-input', 'placeholder': 'Rajkot'}),
            'state':          forms.TextInput(attrs={'class': 'lf-input', 'placeholder': 'Gujarat'}),
            'zipcode':        forms.TextInput(attrs={'class': 'lf-input', 'placeholder': '360001'}),
            'latitude':       forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '22.303894', 'step': '0.000001'}),
            'longitude':      forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '70.801537', 'step': '0.000001'}),
            'total_slots':    forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '90'}),
            'available_slots':forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '0'}),
            'opening_time':   forms.TimeInput(attrs={'class': 'lf-input', 'type': 'time'}),
            'closing_time':   forms.TimeInput(attrs={'class': 'lf-input', 'type': 'time'}),
            'is_operational': forms.CheckboxInput(attrs={'class': 'lf-checkbox'}),
            'parkinglot_image': forms.FileInput(attrs={'class': 'lf-file'}),
        }
class ParkingSlotForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        fields = ['slot_number', 'floor_level', 'slot_type', 'qr_code',
                  'is_available', 'is_reserved',
                  'hourly_rate', 'daily_rate', 'monthly_rate',
                  'dimension_len', 'dimension_wid']
        widgets = {
            'slot_number':      forms.TextInput(attrs={'class': 'lf-input', 'placeholder': 'e.g. A01'}),
            'floor_level':      forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '0'}),
            'slot_type':        forms.Select(attrs={'class': 'lf-input'}),
            'qr_code':          forms.TextInput(attrs={'class': 'lf-input'}),
            'is_available':     forms.CheckboxInput(attrs={'class': 'lf-checkbox'}),
            'is_reserved':      forms.CheckboxInput(attrs={'class': 'lf-checkbox'}),
            'hourly_rate':      forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '40.00', 'step': '0.01'}),
            'daily_rate':       forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '300.00', 'step': '0.01'}),
            'monthly_rate':     forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '3500.00', 'step': '0.01'}),
            'dimension_len': forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '5.00', 'step': '0.01'}),
            'dimension_wid':  forms.NumberInput(attrs={'class': 'lf-input', 'placeholder': '2.50', 'step': '0.01'}),
        }

class BulkSlotForm(forms.ModelForm):
    # Extra field for bulk creation
    number_of_slots = forms.IntegerField(
        min_value=1,
        label="Number of Slots"
    )

    class Meta:
        model = ParkingSlot
        fields = [
            "slot_type",
            "floor_level",
            "hourly_rate",
            "daily_rate",
            "monthly_rate",
            "dimension_len",
            "dimension_wid",
        ]

class ReservationForm(forms.ModelForm):
    vehicle_number = forms.CharField(
        max_length=20,
        validators=[VEHICLE_NUMBER_REGEX],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. GJ01AB1234'})
    )

    class Meta:
        model = Reservation
        fields = ['vehicle_number', 'vehicle_type', 'reservation_type', 'start_time', 'end_time']
        widgets = {
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'reservation_type': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def clean_vehicle_number(self):
        vehicle_number = self.cleaned_data.get('vehicle_number')
        if vehicle_number:
            return vehicle_number.upper()
        return vehicle_number


        
