import base64
import io

# Try to import matplotlib; gracefully handle missing package
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.utils import timezone

from Parkinglot.models import Reservation, Payment, ParkingLot


@login_required
def userDashboardView(request):
    """User dashboard — shows personal reservations and payment stats."""
    user = request.user

    reservations = Reservation.objects.filter(user=user).select_related(
        "parking_slot", "parking_slot__parking_lot"
    ).order_by("-created_at")

    total_reservations = reservations.count()
    paid_count = Payment.objects.filter(user=user, payment_status="completed").count()

    context = {
        "reservations": reservations,
        "total_reservations": total_reservations,
        "paid_reservations": paid_count,
    }
    return render(request, "core/user_dashboard.html", context)


@staff_member_required
def adminDashboardView(request):
    """Admin dashboard — system overview with revenue and slot chart."""
    # Aggregate stats
    total_lots = ParkingLot.objects.count()
    total_reservations = Reservation.objects.count()
    total_revenue = Payment.objects.filter(payment_status="completed").aggregate(
        total=Sum("amount")
    )["total"] or 0

    reservations = Reservation.objects.select_related(
        "user", "parking_slot", "parking_slot__parking_lot"
    ).order_by("-created_at")

    # Build chart: available vs booked slots per lot
    lots = ParkingLot.objects.all()
    lot_names = []
    available_slots = []
    booked_slots = []

    for lot in lots:
        lot_names.append(lot.lot_name)
        avail = lot.get_available_slots_count()
        total = lot.total_slots
        available_slots.append(avail)
        booked_slots.append(total - avail)

    chart_html = ""
    if lot_names and HAS_MATPLOTLIB:
        fig, ax = plt.subplots(figsize=(8, 4))
        x = range(len(lot_names))
        width = 0.35
        ax.bar([i - width / 2 for i in x], available_slots, width, label="Available", color="#28a745")
        ax.bar([i + width / 2 for i in x], booked_slots, width, label="Booked", color="#dc3545")
        ax.set_xticks(list(x))
        ax.set_xticklabels(lot_names, rotation=30, ha="right")
        ax.set_ylabel("Slots")
        ax.set_title("Available vs Booked Slots per Lot")
        ax.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        chart_html = base64.b64encode(buf.getvalue()).decode()
        plt.close(fig)

    context = {
        "total_lots": total_lots,
        "total_reservations": total_reservations,
        "total_revenue": total_revenue,
        "reservations": reservations,
        "chart_image": chart_html,
    }
    return render(request, "core/admin_dashboard.html", context)
