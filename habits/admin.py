from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Habit, UserProfile


class HabitInline(admin.TabularInline):
    model = Habit
    extra = 0
    fields = ("name", "created_at")
    readonly_fields = ("created_at",)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, HabitInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
