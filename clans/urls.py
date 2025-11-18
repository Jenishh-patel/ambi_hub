"""
URL routing for clans app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.clans_list_view, name='clans_list'),
    path('<int:clan_id>/', views.clan_detail_view, name='clan_detail'),
    path('<int:clan_id>/dashboard/', views.clan_dashboard_view, name='clan_dashboard'),
    path('<int:clan_id>/leader-dashboard/', views.leader_dashboard_view, name='leader_dashboard'),
]

