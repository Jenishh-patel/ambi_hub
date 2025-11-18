"""
User account models for Ambitious Hub.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Extended user model with gamification fields."""
    email = models.EmailField(unique=True)
    theme = models.CharField(
        max_length=10,
        choices=[('dark', 'Dark'), ('light', 'Light')],
        default='dark'
    )
    privacy_mode = models.CharField(
        max_length=10,
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    total_xp = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_level(self):
        """Calculate level based on total XP."""
        from ambitioushub.settings import XP_PER_LEVEL, XP_MULTIPLIER
        xp = self.total_xp
        level = 1
        required_xp = XP_PER_LEVEL
        
        while xp >= required_xp:
            xp -= required_xp
            level += 1
            required_xp = int(required_xp * XP_MULTIPLIER)
        
        return level

    def update_streak(self):
        """Update user streak based on last activity."""
        today = timezone.now().date()
        
        if self.last_activity_date is None:
            self.current_streak = 1
            self.last_activity_date = today
        elif self.last_activity_date == today:
            # Already updated today
            pass
        elif (today - self.last_activity_date).days == 1:
            # Consecutive day
            self.current_streak += 1
            self.last_activity_date = today
        else:
            # Streak broken
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            self.current_streak = 1
            self.last_activity_date = today
        
        self.save()

    def get_xp_for_next_level(self):
        """Get XP required for next level."""
        from ambitioushub.settings import XP_PER_LEVEL, XP_MULTIPLIER
        required_xp = XP_PER_LEVEL
        for _ in range(self.current_level - 1):
            required_xp = int(required_xp * XP_MULTIPLIER)
        return required_xp

    def get_xp_progress(self):
        """Get XP progress for current level (0-100)."""
        from ambitioushub.settings import XP_PER_LEVEL, XP_MULTIPLIER
        xp = self.total_xp
        required_xp = XP_PER_LEVEL
        
        for _ in range(self.current_level - 1):
            xp -= required_xp
            required_xp = int(required_xp * XP_MULTIPLIER)
        
        if required_xp == 0:
            return 100
        return int((xp / required_xp) * 100)

    def __str__(self):
        return self.username


class UserFollow(models.Model):
    """User follow relationships."""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

