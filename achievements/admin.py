from django.contrib import admin
from .models import Badge, UserBadge, Milestone, UserMilestone


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'rarity', 'xp_reward', 'condition_type', 'condition_value', 'is_active']
    list_filter = ['rarity', 'is_active']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge', 'earned_at']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'milestone_type', 'milestone_value']


@admin.register(UserMilestone)
class UserMilestoneAdmin(admin.ModelAdmin):
    list_display = ['user', 'milestone', 'achieved_at']

