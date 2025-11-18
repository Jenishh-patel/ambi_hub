"""
Clan Games models for group productivity challenges.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Clan(models.Model):
    """Clan/group for collaborative challenges."""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_clans')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    max_members = models.IntegerField(default=50)
    icon = models.CharField(max_length=50, default='🏆')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_member_count(self):
        return self.members.count()

    def is_full(self):
        return self.get_member_count() >= self.max_members


class ClanMember(models.Model):
    """Clan membership with roles."""
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clan_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    total_contribution_xp = models.IntegerField(default=0)

    class Meta:
        unique_together = ['clan', 'user']

    def __str__(self):
        return f"{self.user.username} in {self.clan.name}"


class ClanJoinRequest(models.Model):
    """Join requests for private clans."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clan_join_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_join_requests'
    )

    class Meta:
        unique_together = ['clan', 'user']

    def __str__(self):
        return f"{self.user.username} -> {self.clan.name}"


class ClanChallenge(models.Model):
    """Challenges created for clans."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='challenges')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges')
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_xp = models.IntegerField(default=1000)
    reward_xp = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.clan.name} - {self.title}"

    def get_progress(self):
        """Get challenge progress percentage."""
        from solo.models import Task
        total_xp = Task.objects.filter(
            user__clan_memberships__clan=self.clan,
            status='completed',
            completed_at__gte=self.start_date,
            completed_at__lte=self.end_date
        ).aggregate(total=models.Sum('awarded_xp'))['total'] or 0
        
        if self.target_xp == 0:
            return 100
        return min(100, int((total_xp / self.target_xp) * 100))


class ClanProgress(models.Model):
    """Individual member progress submissions for clan challenges."""
    challenge = models.ForeignKey(ClanChallenge, on_delete=models.CASCADE, related_name='progress')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clan_progress')
    task = models.ForeignKey('solo.Task', on_delete=models.CASCADE, null=True, blank=True)
    xp_contributed = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['challenge', 'user', 'task']

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"


class ClanMessage(models.Model):
    """Simple chat/comment board for clans."""
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clan_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} in {self.clan.name}"

