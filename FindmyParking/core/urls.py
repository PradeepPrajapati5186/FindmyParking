from django.contrib import admin
from django.urls import path
from core import views
urlpatterns = [
   path('signup/', views.signup_view, name='signup'),
   path('login/', views.login_view, name='login'),
]