import matplotlib.pyplot as plt
from io import BytesIO
from django.utils import timezone
import calendar
from collections import defaultdict

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import Habit, HabitLog
from .forms import HabitForm
from .utils import  get_badges
from .utils import update_streak_and_xp
from habits.models import UserProfile
from datetime import timedelta
import matplotlib

matplotlib.use("Agg")



# -------------------------
# 📈 Monthly Chart (Matplotlib)
# -------------------------
@login_required
def monthly_chart(request):
    today = timezone.localdate()
    year, month = today.year, today.month

    logs = HabitLog.objects.filter(
        habit__user=request.user,
        date__year=year,
        date__month=month,
        completed=True
    )

    days_in_month = calendar.monthrange(year, month)[1]
    daily_count = [0] * days_in_month

    for log in logs:
        daily_count[log.date.day - 1] += 1

    plt.figure(figsize=(10, 4))
    plt.plot(range(1, days_in_month + 1), daily_count, marker='o')
    plt.xlabel("Day")
    plt.ylabel("Completed Habits")
    plt.title("Monthly Habit Progress")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return HttpResponse(buffer.getvalue(), content_type='image/png')


# -------------------------
# 📊 Today Chart (Chart.js data)
# -------------------------
@login_required
def daily_chart_data(request):
    today = timezone.localdate()

    completed = HabitLog.objects.filter(
        habit__user=request.user,
        date=today,
        completed=True
    ).count()

    total = Habit.objects.filter(user=request.user).count()
    remaining = max(total - completed, 0)

    return JsonResponse({
        "labels": ["Completed", "Remaining"],
        "data": [completed, remaining]
    })


# -------------------------
# 🏠 Dashboard (MAIN)
# -------------------------
@login_required
def dashboard(request):
    today = timezone.localdate()
    habits = Habit.objects.filter(user=request.user)

    logs = {
        log.habit_id: log.completed
        for log in HabitLog.objects.filter(
            habit__user=request.user,
            date=today
        )
    }

    if request.method == "POST":
        for habit in habits:
            completed = request.POST.get(f"habit_{habit.id}") == "on"
            HabitLog.objects.update_or_create(
                habit=habit,
                date=today,
                defaults={"completed": completed}
            )
        update_streak_and_xp(request.user)
        return redirect("dashboard")

    completed_habits = []
    incomplete_habits = []

    for habit in habits:
        if logs.get(habit.id):
            completed_habits.append(habit)
        else:
            incomplete_habits.append(habit)

    profile = request.user.userprofile

    return render(request, "habits/dashboard.html", {
        "completed_habits": completed_habits,
        "incomplete_habits": incomplete_habits,
        "logs": logs,
        "streak": profile.current_streak,
        "xp":profile.xp,
        "level":profile.level,
        "profile": profile,
        "username": request.user.first_name or request.user.username,
    })




# -------------------------
# ➕ Add Habit
# -------------------------
@login_required
def add_habit(request):
    if request.method == "POST":
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            return redirect("dashboard")
    else:
        form = HabitForm()

    return render(request, "habits/add_habit.html", {"form": form})


# -------------------------
# ✏️ Edit Habit
# -------------------------
@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = HabitForm(instance=habit)

    return render(request, "habits/edit_habit.html", {"form": form})


# -------------------------
# 🗑️ Delete Habit
# -------------------------
@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    if request.method == "POST":
        habit.delete()
        return redirect("dashboard")

    return render(request, "habits/delete_habit.html", {"habit": habit})


# -------------------------
# 📆 Weekly Analytics
# -------------------------
@login_required
def weekly_analytics(request):
    today = timezone.localdate()
    data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = HabitLog.objects.filter(
            habit__user=request.user,
            date=day,
            completed=True
        ).count()

        data.append({
            "day": day.strftime("%a"),
            "count": count
        })

    return render(request, "habits/weekly.html", {"data": data})


# -------------------------
# 🔥 Heatmap Helpers
# -------------------------
def get_color(intensity):
    if intensity == 0:
        return "#161b22"
    elif intensity <= 0.25:
        return "#0e4429"
    elif intensity <= 0.5:
        return "#006d32"
    elif intensity <= 0.75:
        return "#26a641"
    else:
        return "#39d353"


# -------------------------
# 🟩 Heatmap View
# -------------------------
@login_required
def heatmap(request):
    user = request.user
    total_habits = Habit.objects.filter(user=user).count()

    today = timezone.localdate()
    start_date = today - timedelta(days=365)

    completed_logs = (
        HabitLog.objects
        .filter(habit__user=user, completed=True)
        .values("date")
        .annotate(count=Count("id"))
    )

    completed_map = {log["date"]: log["count"] for log in completed_logs}

    heatmap_data = []
    current = start_date

    while current <= today:
        completed = completed_map.get(current, 0)
        intensity = completed / total_habits if total_habits else 0

        heatmap_data.append({
            "date": current,
            "weekday": current.weekday(),
            "week": current.isocalendar().week,
            "month": current.strftime("%b"),
            "color": get_color(intensity),
            "completed": completed,
        })

        current += timedelta(days=1)

    return render(request, "habits/heatmap.html", {
        "heatmap": heatmap_data
    })


@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        selected_avatar = request.POST.get("avatar")
        if selected_avatar:
            profile.avatar = selected_avatar
            profile.save()
            return redirect("profile")

    total_habits = Habit.objects.filter(user=request.user).count()
    total_completions = HabitLog.objects.filter(
        habit__user = request.user,
        completed=True
    ).count()

    success_rate = (
        int((total_completions / (total_habits * 10)) * 100)
        if total_habits > 0 else 0
    )

    xp_for_next_level = profile.level * 100
    xp_progress = int((profile.xp / xp_for_next_level) * 100)

    top_habit = (
        HabitLog.objects.filter(habit__user=request.user, completed=True).values("habit__name")
        .annotate(c=Count("id")).order_by("-c").first()
    )

    avatars = [
        "avatar1.gif",
        "avatar2.gif",
        "avatar3.gif",
        "avatar4.gif",
    ]

    return render(request, "habits/profile.html", {
        "user": request.user,
        "profile": profile,
        "success_rate": success_rate,
        "xp_progress": min(xp_progress, 100),
        "top_habit": top_habit["habit__name"] if top_habit else None,
        "total_habits": total_habits,
        "total_completions": total_completions,
        "avatars": avatars,
    })