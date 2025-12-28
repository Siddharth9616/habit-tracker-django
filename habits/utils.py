from django.utils import timezone
from .models import Habit, HabitLog, UserProfile

from datetime import timedelta


BASE_XP = 10

def update_streak_and_xp(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    today = timezone.localdate()

    # Count completed habits today
    completed_today = HabitLog.objects.filter(
        habit__user=user,
        date=today,
        completed=True
    ).count()

    # If nothing completed → do nothing
    if completed_today == 0:
        return profile

    # 🚫 Prevent double XP on same day
    if profile.last_active_date == today:
        return profile

    # ---------- STREAK LOGIC ----------
    if profile.last_active_date == today - timedelta(days=1):
        profile.current_streak += 1
    else:
        profile.current_streak = 1

    profile.last_active_date = today
    profile.best_streak = max(profile.best_streak, profile.current_streak)

    # ---------- XP LOGIC ----------
    gained_xp = completed_today * BASE_XP
    profile.xp += gained_xp

    # ---------- LEVEL ----------
    profile.level = (profile.xp // 100) + 1

    profile.save()
    return profile



def get_badges(streak):
    badges = []
    if streak >= 7:
        badges.append("🥉 Bronze Streak (7 days)")
    if streak >= 30:
        badges.append("🥈 Silver Streak (30 days)")
    if streak >= 100:
        badges.append("🥇 Gold Streak (100 days)")
    return badges