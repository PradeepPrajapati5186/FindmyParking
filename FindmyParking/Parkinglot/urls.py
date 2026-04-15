from django.contrib import admin
from django.urls import path
from . import views
from . import dashboard_views

urlpatterns = [
    path('admin_dashboard/', dashboard_views.adminDashboardView, name='admin_dashboard'),
    path('user_dashboard/', dashboard_views.userDashboardView, name='user_dashboard'),
    path('parkinglots/', views.parkingLotsView, name='parking_lots'),
    path('parkingslots/<int:lot_id>/', views.parkingSlotsView, name='parking_slots'),
    path('add_parkinglot/', views.parkingLotFormView, name='add_parkinglot'),
    path('add_slot/<int:lot_id>/', views.add_slot_view, name='add_slot'),
    path('bulk_add_slots/<int:lot_id>/', views.bulk_add_slots, name='bulk_add_slots'),
    path('delete_slot/<int:slot_id>/', views.delete_slot_view, name='delete_slot'),
    path('delete_lot/<int:lot_id>/', views.delete_lot_view, name='delete_lot'),
    path('reservation/create/<int:slot_id>/', views.create_reservation, name='create_reservation'),
    path('reservation/success/<int:reservation_id>/', views.reservation_success, name='reservation_success'),
    path('start_reservation/<int:slot_id>/', views.start_reservation, name='start_reservation'),
    path("reservation/<int:reservation_id>/cancel/", views.cancel_reservation, name="cancel_reservation"),
    path("reservation/<int:reservation_id>/pay/", views.pay_reservation, name="pay_reservation"),
]

