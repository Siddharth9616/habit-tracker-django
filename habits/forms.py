from django import forms
from .models import Habit
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name']


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("⚠️ Username already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("⚠️ Email already registered")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError("❌ Passwords do not match")

        return cleaned_data
