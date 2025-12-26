from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-habit/', views.add_habit, name='add_habit'),
    path('monthly-chart/', views.monthly_chart, name='monthly_chart'),
    path('daily-data/', views.daily_chart_data, name='daily_data'),
    path('edit-habit/<int:habit_id>/', views.edit_habit, name='edit_habit'),
    path('delete-habit/<int:habit_id>/', views.delete_habit, name='delete_habit'),
    path('weekly/', views.weekly_analytics, name='weekly_analytics'),
    path('heatmap/', views.heatmap, name='heatmap'),
    path("api/daily-chart/", views.daily_chart_data, name="daily_chart_data"),
    path("profile/", views.profile, name="profile"),


]
