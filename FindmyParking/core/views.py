from django.shortcuts import render
from .forms import SignupForm, LoginForm
from django.shortcuts import redirect
from django.contrib.auth import login,authenticate


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
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if user.user_type == "owner":
                    return redirect("owner_dashboard")
                else:
                    return redirect("user_dashboard")
            else:
                return render(request, 'core/login.html', {'form': form})
        else:
            return render(request, 'core/login.html', {'form': form})
    form = LoginForm()
    return render(request, 'core/login.html', {'form': form})