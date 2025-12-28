from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def user_login(request):
    next_url = request.GET.get("next", "dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "auth/login.html")



def user_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # 1️⃣ Password match check
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        # 2️⃣ Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        # 3️⃣ Email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address")
            return redirect("signup")

        # 4️⃣ Email uniqueness
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        # 5️⃣ Password strength
        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect("signup")

        # 6️⃣ Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        login(request, user)
        messages.success(request, "Account created successfully 🎉")
        return redirect("dashboard")

    return render(request, "auth/signup.html")


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect("login")
