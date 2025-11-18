"""
API URL routing for accounts app.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('profile/', api_views.ProfileAPIView.as_view(), name='api_profile'),
    path('dashboard-stats/', api_views.DashboardStatsAPIView.as_view(), name='api_dashboard_stats'),
    path('followers/', api_views.FollowersAPIView.as_view(), name='api_followers'),
    path('following/', api_views.FollowingAPIView.as_view(), name='api_following'),
    path('leaderboard/', api_views.LeaderboardAPIView.as_view(), name='api_leaderboard'),
    path('feed/', api_views.FeedAPIView.as_view(), name='api_feed'),
]

