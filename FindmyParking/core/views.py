from django.shortcuts import render
from .forms import SignupForm, LoginForm
from django.shortcuts import redirect
from django.contrib.auth import login


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'core/signup.html', {'form': form})
    else:
        form = SignupForm()
        return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = LoginForm()
        return render(request, 'core/login.html', {'form': form})