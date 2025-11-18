"""
Analytics and reporting models.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserReport(models.Model):
    """Generated user reports."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=50)  # e.g., 'daily', 'weekly', 'monthly', 'custom'
    start_date = models.DateField()
    end_date = models.DateField()
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.report_type} ({self.start_date} to {self.end_date})"

