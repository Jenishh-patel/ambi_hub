"""
API URL routing for adminpanel app.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('platform-stats/', api_views.PlatformStatsAPIView.as_view(), name='api_platform_stats'),
    path('users/', api_views.UsersAPIView.as_view(), name='api_users'),
    path('clans/', api_views.ClansAPIView.as_view(), name='api_clans'),
    path('global-challenges/', api_views.GlobalChallengesAPIView.as_view(), name='api_global_challenges'),
]

