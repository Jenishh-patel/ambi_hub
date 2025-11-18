"""
Achievements views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def achievements_view(request):
    """Achievements page."""
    return render(request, 'achievements/achievements.html')

