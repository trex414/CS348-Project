from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome'),
    path('create_account/', views.create_account, name='create_account'),
        path('login/', views.login, name='login'),
    path('main/', views.main_page, name='main'),
    path('edit/<int:entry_id>/', views.edit_food, name='edit_food'),
    path('remove-food/', views.remove_food, name='remove_food'),
    path('day-planner/', views.day_planner, name='day_planner'),
    path('add-meal/', views.add_meal, name='add_meal'),
    path('add-to-plan/', views.add_to_plan, name='add_to_plan'),
    path('remove-from-plan/<int:plan_id>/', views.remove_from_plan, name='remove_from_plan'),
    path('export-day-plan/', views.export_day_plan, name='export_day_plan'),
    path('export-all-entries/', views.export_all_entries, name='export_all_entries'),
    path('move_plan_entry/<int:plan_id>/', views.move_plan_entry, name='move_plan_entry'),
]
