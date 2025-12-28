from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit', 'date')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    avatar = models.CharField(
        max_length=100,
        default="avatar1.png"
    )

    def __str__(self):
        return self.user.username
