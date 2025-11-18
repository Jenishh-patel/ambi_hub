"""
Workout views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def workout_view(request):
    """Main workout page."""
    return render(request, 'workout/workout.html')

