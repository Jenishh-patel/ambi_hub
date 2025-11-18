from django.contrib import admin
from .models import (
    Clan, ClanMember, ClanJoinRequest,
    ClanChallenge, ClanProgress, ClanMessage
)


@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'visibility', 'max_members', 'created_at']
    list_filter = ['visibility', 'created_at']


@admin.register(ClanMember)
class ClanMemberAdmin(admin.ModelAdmin):
    list_display = ['clan', 'user', 'role', 'total_contribution_xp', 'joined_at']
    list_filter = ['role', 'clan']


@admin.register(ClanJoinRequest)
class ClanJoinRequestAdmin(admin.ModelAdmin):
    list_display = ['clan', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']


@admin.register(ClanChallenge)
class ClanChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'clan', 'status', 'target_xp', 'end_date']
    list_filter = ['status', 'clan']


@admin.register(ClanProgress)
class ClanProgressAdmin(admin.ModelAdmin):
    list_display = ['challenge', 'user', 'xp_contributed', 'submitted_at']
    list_filter = ['challenge']


@admin.register(ClanMessage)
class ClanMessageAdmin(admin.ModelAdmin):
    list_display = ['clan', 'user', 'created_at']
    list_filter = ['clan', 'created_at']

