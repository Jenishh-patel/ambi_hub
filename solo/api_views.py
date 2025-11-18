"""
API views for solo app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from .models import Category, Task, DailySummary
from achievements.utils import check_badges, check_milestones
import random


class CategoryAPIView(APIView):
    """List and create categories."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = Category.objects.filter(
            models.Q(user=request.user) | models.Q(user__isnull=True)
        ).distinct()
        return Response({
            'categories': [{
                'id': cat.id,
                'name': cat.name,
                'category_type': cat.category_type,
                'icon': cat.icon,
                'color': cat.color,
                'xp_multiplier': cat.xp_multiplier,
            } for cat in categories]
        })
    
    def post(self, request):
        name = request.data.get('name')
        category_type = request.data.get('category_type', 'custom')
        icon = request.data.get('icon', '📝')
        color = request.data.get('color', '#3B82F6')
        xp_multiplier = float(request.data.get('xp_multiplier', 1.0))
        
        category = Category.objects.create(
            user=request.user,
            name=name,
            category_type=category_type,
            icon=icon,
            color=color,
            xp_multiplier=xp_multiplier
        )
        
        return Response({
            'id': category.id,
            'name': category.name,
            'category_type': category.category_type,
            'icon': category.icon,
            'color': category.color,
            'xp_multiplier': category.xp_multiplier,
        }, status=status.HTTP_201_CREATED)


class CategoryDetailAPIView(APIView):
    """Get, update, delete category."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        if category.user and category.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'id': category.id,
            'name': category.name,
            'category_type': category.category_type,
            'icon': category.icon,
            'color': category.color,
            'xp_multiplier': category.xp_multiplier,
        })
    
    def put(self, request, category_id):
        category = get_object_or_404(Category, id=category_id, user=request.user)
        category.name = request.data.get('name', category.name)
        category.icon = request.data.get('icon', category.icon)
        category.color = request.data.get('color', category.color)
        category.xp_multiplier = float(request.data.get('xp_multiplier', category.xp_multiplier))
        category.save()
        
        return Response({
            'id': category.id,
            'name': category.name,
            'category_type': category.category_type,
            'icon': category.icon,
            'color': category.color,
            'xp_multiplier': category.xp_multiplier,
        })
    
    def delete(self, request, category_id):
        category = get_object_or_404(Category, id=category_id, user=request.user)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskAPIView(APIView):
    """List and create tasks."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        category_id = request.GET.get('category')
        status_filter = request.GET.get('status')
        date_filter = request.GET.get('date')  # Filter by specific date
        days_filter = request.GET.get('days')  # Filter by last N days
        
        tasks = Task.objects.filter(user=request.user)
        
        if category_id:
            tasks = tasks.filter(category_id=category_id)
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        # Date filtering
        if date_filter:
            # Filter by specific date (today)
            from datetime import datetime
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            tasks = tasks.filter(created_at__date=filter_date)
        elif days_filter:
            # Filter by last N days
            from datetime import timedelta
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=int(days_filter))
            tasks = tasks.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        
        tasks = tasks.select_related('category').order_by('-created_at')
        
        return Response({
            'tasks': [{
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'category': {
                    'id': task.category.id,
                    'name': task.category.name,
                    'icon': task.category.icon,
                    'color': task.category.color,
                },
                'status': task.status,
                'duration_minutes': task.duration_minutes,
                'gym_reps': task.gym_reps,
                'gym_weight': task.gym_weight,
                'coding_hours': task.coding_hours,
                'base_xp': task.base_xp,
                'awarded_xp': task.awarded_xp,
                'created_at': task.created_at.isoformat(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'due_date': task.due_date.isoformat() if task.due_date else None,
            } for task in tasks]
        })
    
    def post(self, request):
        category = get_object_or_404(Category, id=request.data.get('category_id'))
        title = request.data.get('title')
        description = request.data.get('description', '')
        # Base XP is auto-calculated, default to 10
        base_xp = 10
        duration_minutes = request.data.get('duration_minutes')
        coding_hours = request.data.get('coding_hours')
        due_date = request.data.get('due_date')
        
        task = Task.objects.create(
            user=request.user,
            category=category,
            title=title,
            description=description,
            base_xp=base_xp,  # Auto-calculated, default 10
            duration_minutes=int(request.data.get('duration_minutes')) if request.data.get('duration_minutes') else None,
            # Gym fields - only duration and notes (stored in description)
            coding_hours=float(request.data.get('coding_hours')) if request.data.get('coding_hours') else None,
            coding_language=request.data.get('coding_language', ''),
            academics_subject=request.data.get('academics_subject', ''),
            academics_topic=request.data.get('academics_topic', ''),
            content_type=request.data.get('content_type', ''),
            content_proof_link=request.data.get('content_proof_link', ''),
            reading_book=request.data.get('reading_book', ''),
            reading_pages=int(request.data.get('reading_pages')) if request.data.get('reading_pages') else None,
            habit_name=request.data.get('habit_name', ''),
            habit_streak_target=int(request.data.get('habit_streak_target')) if request.data.get('habit_streak_target') else None,
            due_date=due_date if due_date else None,
        )
        
        return Response({
            'id': task.id,
            'title': task.title,
            'category': {
                'id': task.category.id,
                'name': task.category.name,
            },
            'status': task.status,
            'base_xp': task.base_xp,
        }, status=status.HTTP_201_CREATED)


class TaskDetailAPIView(APIView):
    """Get, update, delete task."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        return Response({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'category': {
                'id': task.category.id,
                'name': task.category.name,
                'icon': task.category.icon,
                'color': task.category.color,
            },
            'status': task.status,
            'duration_minutes': task.duration_minutes,
            'gym_reps': task.gym_reps,
            'gym_weight': task.gym_weight,
            'coding_hours': task.coding_hours,
            'base_xp': task.base_xp,
            'awarded_xp': task.awarded_xp,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'due_date': task.due_date.isoformat() if task.due_date else None,
        })
    
    def put(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        if task.status == 'completed':
            return Response({'error': 'Cannot edit completed task'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.title = request.data.get('title', task.title)
        task.description = request.data.get('description', task.description)
        task.base_xp = int(request.data.get('base_xp', task.base_xp))
        task.duration_minutes = request.data.get('duration_minutes')
        task.gym_reps = request.data.get('gym_reps')
        task.gym_weight = request.data.get('gym_weight')
        task.coding_hours = request.data.get('coding_hours')
        task.due_date = request.data.get('due_date')
        
        if request.data.get('category_id'):
            task.category = get_object_or_404(Category, id=request.data.get('category_id'))
        
        task.save()
        
        return Response({
            'id': task.id,
            'title': task.title,
            'status': task.status,
        })
    
    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompleteTaskAPIView(APIView):
    """Complete a task and award XP."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        if task.status == 'completed':
            return Response({'error': 'Task already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_level = request.user.current_level
        task.complete()
        new_level = request.user.current_level
        
        # Check for badges and milestones
        badges_earned = check_badges(request.user)
        milestone_achieved = None
        if new_level > old_level:
            milestone_achieved = check_milestones(request.user, 'level', new_level)
        
        return Response({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'awarded_xp': task.awarded_xp,
            },
            'user': {
                'total_xp': request.user.total_xp,
                'current_level': request.user.current_level,
                'xp_progress': request.user.get_xp_progress(),
            },
            'leveled_up': new_level > old_level,
            'badges_earned': badges_earned,
            'milestone_achieved': milestone_achieved,
        })


class DailySummaryAPIView(APIView):
    """Get daily summary."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        date_str = request.GET.get('date')
        if date_str:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        summary, created = DailySummary.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={
                'tasks_completed': 0,
                'xp_earned': 0,
                'categories_worked': [],
            }
        )
        
        # Update summary from actual tasks
        tasks = Task.objects.filter(
            user=request.user,
            status='completed',
            completed_at__date=date
        )
        summary.tasks_completed = tasks.count()
        summary.xp_earned = sum(task.awarded_xp for task in tasks)
        summary.categories_worked = list(tasks.values_list('category__name', flat=True).distinct())
        summary.save()
        
        return Response({
            'date': summary.date.isoformat(),
            'tasks_completed': summary.tasks_completed,
            'xp_earned': summary.xp_earned,
            'categories_worked': summary.categories_worked,
        })


class MotivationalQuoteAPIView(APIView):
    """Get a random motivational quote."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "It is during our darkest moments that we must focus to see the light. - Aristotle",
            "The way to get started is to quit talking and begin doing. - Walt Disney",
            "Don't let yesterday take up too much of today. - Will Rogers",
            "You learn more from failure than from success. - Unknown",
            "If you are working on something exciting that you really care about, you don't have to be pushed. - Steve Jobs",
            "People who are crazy enough to think they can change the world, are the ones who do. - Rob Siltanen",
            "We may encounter many defeats but we must not be defeated. - Maya Angelou",
        ]
        return Response({
            'quote': random.choice(quotes)
        })

