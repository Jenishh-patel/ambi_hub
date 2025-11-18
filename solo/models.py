"""
Solo Leveling models for individual productivity tracking.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Predefined categories
CATEGORY_CHOICES = [
    ('coding', 'Coding'),
    ('gym', 'Gym'),
    ('academics', 'Academics'),
    ('content', 'Content Creation'),
    ('reading', 'Reading'),
    ('habits', 'Habits'),
    ('custom', 'Custom'),
]


class Category(models.Model):
    """Task categories (predefined + custom)."""
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    icon = models.CharField(max_length=50, default='📝')
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    xp_multiplier = models.FloatField(default=1.0)  # XP multiplier for this category
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'user', 'category_type']

    def __str__(self):
        return self.name


class Task(models.Model):
    """Individual tasks/entries for solo leveling."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Task-specific fields
    duration_minutes = models.IntegerField(null=True, blank=True)  # For timers
    gym_reps = models.IntegerField(null=True, blank=True)
    gym_weight = models.FloatField(null=True, blank=True)
    gym_sets = models.IntegerField(null=True, blank=True)
    gym_exercise = models.CharField(max_length=100, blank=True)  # Exercise name
    coding_hours = models.FloatField(null=True, blank=True)
    coding_language = models.CharField(max_length=50, blank=True)
    academics_subject = models.CharField(max_length=100, blank=True)
    academics_topic = models.CharField(max_length=200, blank=True)
    content_type = models.CharField(max_length=50, blank=True)  # video/edit/script
    content_proof_link = models.URLField(blank=True)
    reading_book = models.CharField(max_length=200, blank=True)
    reading_pages = models.IntegerField(null=True, blank=True)
    habit_name = models.CharField(max_length=100, blank=True)
    habit_streak_target = models.IntegerField(null=True, blank=True)
    proof_file = models.FileField(upload_to='proofs/', null=True, blank=True)
    
    # XP and rewards
    base_xp = models.IntegerField(default=10)
    awarded_xp = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)

    def calculate_xp(self):
        """Calculate XP for this task based on category and task type."""
        base = self.base_xp
        multiplier = self.category.xp_multiplier
        
        # Bonus XP for different task types
        if self.duration_minutes:
            base += int(self.duration_minutes / 10)  # 1 XP per 10 minutes
        if self.gym_reps:
            base += int(self.gym_reps / 5)  # 1 XP per 5 reps
        if self.coding_hours:
            base += int(self.coding_hours * 10)  # 10 XP per hour
        
        return int(base * multiplier)

    def complete(self):
        """Mark task as completed and award XP."""
        if self.status == 'completed':
            return
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.awarded_xp = self.calculate_xp()
        
        # Award XP to user
        self.user.total_xp += self.awarded_xp
        self.user.current_level = self.user.calculate_level()
        self.user.update_streak()
        self.user.save()
        
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class DailySummary(models.Model):
    """Daily summary of user activity."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField()
    tasks_completed = models.IntegerField(default=0)
    xp_earned = models.IntegerField(default=0)
    categories_worked = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        verbose_name_plural = 'Daily Summaries'

    def __str__(self):
        return f"{self.user.username} - {self.date}"

