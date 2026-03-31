from django.core.management.base import BaseCommand
from django.core.files import File
from io import BytesIO
import qrcode
from Parkinglot.models import ParkingSlot

class Command(BaseCommand):
    help = "Regenerate QR codes for slots (optionally by lot). Skips existing unless --force is used."

    def add_arguments(self, parser):
        parser.add_argument(
            '--lot_id',
            type=int,
            help='ID of the parking lot to regenerate QR codes for'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if a slot already has a QR code'
        )

    def handle(self, *args, **options):
        lot_id = options['lot_id']
        force = options['force']

        if lot_id:
            slots = ParkingSlot.objects.filter(parking_lot_id=lot_id)
            self.stdout.write(self.style.WARNING(f"Regenerating QR codes for Lot {lot_id}..."))
        else:
            slots = ParkingSlot.objects.all()
            self.stdout.write(self.style.WARNING("Regenerating QR codes for ALL lots..."))

        for slot in slots:
            # Skip if QR already exists and not forcing
            if slot.qr_code and slot.qr_code.name and not force:
                self.stdout.write(self.style.NOTICE(
                    f"Skipping Slot {slot.slot_number} in Lot {slot.parking_lot.id} (already has QR)"
                ))
                continue

            # Generate QR code
            qr_data = f"Lot-{slot.parking_lot.id}-Slot-{slot.slot_number}"
            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            filename = f"lot{slot.parking_lot.id}_slot{slot.slot_number}.png"

            slot.qr_code.save(filename, File(buffer), save=True)
            self.stdout.write(self.style.SUCCESS(
                f"Generated QR for Slot {slot.slot_number} in Lot {slot.parking_lot.id}"
            ))
