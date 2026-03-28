from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('owner_dashboard/', views.ownerDashboardView, name='owner_dashboard'),
    path('user_dashboard/', views.userDashboardView, name='user_dashboard'),
    path('parkinglots/', views.parkingLotsView, name='parking_lots'),
    path('parkingslots/<int:lot_id>/', views.parkingSlotsView, name='parking_slots'),
    path('add_parkinglot/', views.parkingLotFormView, name='add_parkinglot'),
    path('add_slot/<int:lot_id>/', views.add_slot_view, name='add_slot'),
    path('bulk_add_slots/<int:lot_id>/', views.bulk_add_slots, name='bulk_add_slots'),
]