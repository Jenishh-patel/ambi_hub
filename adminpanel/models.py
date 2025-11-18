"""
Admin panel models for platform management.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class GlobalChallenge(models.Model):
    """Platform-wide challenges."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    target_xp = models.IntegerField(default=10000)
    reward_xp = models.IntegerField(default=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PlatformAnalytics(models.Model):
    """Platform-wide analytics snapshots."""
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    total_tasks_completed = models.IntegerField(default=0)
    total_xp_earned = models.IntegerField(default=0)
    total_clans = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Platform Analytics'

    def __str__(self):
        return f"Analytics - {self.date}"

