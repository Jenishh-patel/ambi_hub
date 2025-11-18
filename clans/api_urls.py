"""
API URL routing for clans app.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ClanAPIView.as_view(), name='api_clans'),
    path('<int:clan_id>/', api_views.ClanDetailAPIView.as_view(), name='api_clan_detail'),
    path('<int:clan_id>/join/', api_views.JoinClanAPIView.as_view(), name='api_join_clan'),
    path('<int:clan_id>/leave/', api_views.LeaveClanAPIView.as_view(), name='api_leave_clan'),
    path('<int:clan_id>/members/', api_views.ClanMembersAPIView.as_view(), name='api_clan_members'),
    path('<int:clan_id>/challenges/', api_views.ClanChallengesAPIView.as_view(), name='api_clan_challenges'),
    path('<int:clan_id>/leaderboard/', api_views.ClanLeaderboardAPIView.as_view(), name='api_clan_leaderboard'),
    path('<int:clan_id>/messages/', api_views.ClanMessagesAPIView.as_view(), name='api_clan_messages'),
    path('<int:clan_id>/progress/', api_views.ClanProgressAPIView.as_view(), name='api_clan_progress'),
    path('<int:clan_id>/join-requests/', api_views.ClanJoinRequestsAPIView.as_view(), name='api_clan_join_requests'),
    path('<int:clan_id>/approve-request/<int:user_id>/', api_views.ApproveJoinRequestAPIView.as_view(), name='api_approve_join_request'),
    path('<int:clan_id>/remove-member/<int:user_id>/', api_views.RemoveMemberAPIView.as_view(), name='api_remove_member'),
    path('<int:clan_id>/promote-member/<int:user_id>/', api_views.PromoteMemberAPIView.as_view(), name='api_promote_member'),
]

