from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'user_type', 'firstname', 'lastname', 'phonenumber', 'profile_image')
        widgets = {
            'password1':forms.PasswordInput(),
            'password2':forms.PasswordInput(),
        }
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())