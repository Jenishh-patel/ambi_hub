"""
URL routing for achievements app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.achievements_view, name='achievements'),
]

