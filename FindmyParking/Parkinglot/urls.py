from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('owner_dashboard/', views.ownerDashboardView, name='owner_dashboard'),
    path('user_dashboard/', views.userDashboardView, name='user_dashboard'),
]