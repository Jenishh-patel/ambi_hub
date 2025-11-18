"""
URL routing for solo app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('solo/', views.solo_leveling_view, name='solo_leveling'),
    path('task/<int:task_id>/', views.task_detail_view, name='task_detail'),
]

