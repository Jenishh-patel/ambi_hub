"""
Solo Leveling views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from .models import Category, Task, DailySummary
from achievements.models import Badge, UserBadge
from achievements.utils import check_badges


@login_required
def dashboard_view(request):
    """Main dashboard."""
    return render(request, 'solo/dashboard.html')


@login_required
def solo_leveling_view(request):
    """Solo leveling main page."""
    categories = Category.objects.filter(
        models.Q(user=request.user) | models.Q(user__isnull=True)
    ).distinct()
    return render(request, 'solo/solo_leveling.html', {'categories': categories})


@login_required
def task_detail_view(request, task_id):
    """Task detail page."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    return render(request, 'solo/task_detail.html', {'task': task})

