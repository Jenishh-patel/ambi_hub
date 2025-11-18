"""
Utility functions for achievements and badges.
"""
from .models import Badge, UserBadge, Milestone, UserMilestone
from solo.models import Task


def check_badges(user):
    """Check and award badges to user."""
    badges_earned = []
    active_badges = Badge.objects.filter(is_active=True)
    
    for badge in active_badges:
        if UserBadge.objects.filter(user=user, badge=badge).exists():
            continue
        
        earned = False
        
        if badge.condition_type == 'level_reached':
            earned = user.current_level >= badge.condition_value
        elif badge.condition_type == 'streak_days':
            earned = user.current_streak >= badge.condition_value
        elif badge.condition_type == 'tasks_completed':
            count = Task.objects.filter(user=user, status='completed').count()
            earned = count >= badge.condition_value
        elif badge.condition_type == 'total_xp':
            earned = user.total_xp >= badge.condition_value
        
        if earned:
            user_badge = UserBadge.objects.create(user=user, badge=badge)
            user.total_xp += badge.xp_reward
            user.save()
            badges_earned.append({
                'id': badge.id,
                'name': badge.name,
                'icon': badge.icon,
                'rarity': badge.rarity,
                'xp_reward': badge.xp_reward,
            })
    
    return badges_earned


def check_milestones(user, milestone_type, value):
    """Check and award milestones to user."""
    milestones = Milestone.objects.filter(
        milestone_type=milestone_type,
        milestone_value=value
    )
    
    for milestone in milestones:
        if not UserMilestone.objects.filter(user=user, milestone=milestone).exists():
            UserMilestone.objects.create(user=user, milestone=milestone)
            return {
                'id': milestone.id,
                'name': milestone.name,
                'message': milestone.celebration_message,
            }
    
    return None

