"""
Achievements and badges system.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

RARITY_CHOICES = [
    ('common', 'Common'),
    ('uncommon', 'Uncommon'),
    ('rare', 'Rare'),
    ('epic', 'Epic'),
    ('legendary', 'Legendary'),
]


class Badge(models.Model):
    """Badge definitions."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏅')
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    xp_reward = models.IntegerField(default=50)
    condition_type = models.CharField(max_length=50)  # e.g., 'level_reached', 'streak_days', 'tasks_completed'
    condition_value = models.IntegerField()  # e.g., level 10, 30 days streak, 100 tasks
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """User badge achievements."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    earned_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class Milestone(models.Model):
    """Milestone definitions for celebrations."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    milestone_type = models.CharField(max_length=50)  # e.g., 'level', 'xp', 'streak', 'tasks'
    milestone_value = models.IntegerField()
    celebration_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserMilestone(models.Model):
    """User milestone achievements."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='milestones')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='user_milestones')
    achieved_at = models.DateTimeField(auto_now_add=True)
    certificate_generated = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'milestone']

    def __str__(self):
        return f"{self.user.username} - {self.milestone.name}"

