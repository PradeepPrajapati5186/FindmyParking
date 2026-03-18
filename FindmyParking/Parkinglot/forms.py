from django import forms
from .models import ParkingLot, ParkingSlot, Vehicle   

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