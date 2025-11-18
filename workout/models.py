"""
Workout and Progressive Overload Tracking models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

EXERCISE_CATEGORIES = [
    ('push', 'Push'),
    ('pull', 'Pull'),
    ('legs', 'Legs'),
    ('core', 'Core'),
    ('cardio', 'Cardio'),
    ('custom', 'Custom'),
]


class Exercise(models.Model):
    """Exercise library - default and custom exercises."""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=EXERCISE_CATEGORIES, default='custom')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_exercises'
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'user', 'category']
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def get_personal_record(self, user):
        """Get personal record for this exercise for a user."""
        try:
            return PersonalRecord.objects.get(exercise=self, user=user)
        except PersonalRecord.DoesNotExist:
            return None


class WorkoutSession(models.Model):
    """Workout session - contains multiple sets."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    total_volume = models.FloatField(default=0)  # Sum of all set volumes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date']

    def calculate_total_volume(self):
        """Calculate total volume for this session."""
        total = sum(set_entry.volume for set_entry in self.sets.all())
        self.total_volume = total
        self.save()
        return total

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class SetEntry(models.Model):
    """Individual set entry within a workout session."""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='set_entries')
    reps = models.IntegerField()
    weight = models.FloatField()  # in kg
    rpe = models.IntegerField(null=True, blank=True, help_text="Rate of Perceived Exertion (1-10)")
    volume = models.FloatField(default=0)  # reps * weight
    set_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['set_number']
        unique_together = ['session', 'exercise', 'set_number']

    def save(self, *args, **kwargs):
        """Calculate volume on save."""
        self.volume = self.reps * self.weight
        super().save(*args, **kwargs)
        
        # Update session total volume
        self.session.calculate_total_volume()
        
        # Check for personal record
        self.check_personal_record()

    def check_personal_record(self):
        """Check and update personal record if this is a new max weight."""
        pr, created = PersonalRecord.objects.get_or_create(
            exercise=self.exercise,
            user=self.session.user,
            defaults={'max_weight': self.weight, 'date_achieved': self.session.date}
        )
        
        if not created and self.weight > pr.max_weight:
            pr.max_weight = self.weight
            pr.date_achieved = self.session.date
            pr.save()

    def __str__(self):
        return f"{self.exercise.name} - {self.reps}x{self.weight}kg"


class PersonalRecord(models.Model):
    """Personal records for exercises."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_records')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='personal_records')
    max_weight = models.FloatField()
    date_achieved = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'exercise']
        ordering = ['-max_weight']

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name}: {self.max_weight}kg"

