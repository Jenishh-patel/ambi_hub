"""
API views for accounts app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import UserFollow
from solo.models import Task, DailySummary
from achievements.models import UserBadge

User = get_user_model()


class ProfileAPIView(APIView):
    """Get user profile data."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else None,
            'theme': user.theme,
            'privacy_mode': user.privacy_mode,
            'total_xp': user.total_xp,
            'current_level': user.current_level,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'xp_progress': user.get_xp_progress(),
            'xp_for_next_level': user.get_xp_for_next_level(),
        })


class DashboardStatsAPIView(APIView):
    """Get dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Today's stats
        today_tasks = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__date=today
        )
        today_xp = sum(task.awarded_xp for task in today_tasks)
        
        # Weekly stats
        week_tasks = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__date__gte=week_ago
        )
        week_xp = sum(task.awarded_xp for task in week_tasks)
        
        return Response({
            'total_xp': user.total_xp,
            'current_level': user.current_level,
            'current_streak': user.current_streak,
            'xp_progress': user.get_xp_progress(),
            'xp_for_next_level': user.get_xp_for_next_level(),
            'today_xp': today_xp,
            'today_tasks': today_tasks.count(),
            'week_xp': week_xp,
            'week_tasks': week_tasks.count(),
            'total_badges': UserBadge.objects.filter(user=user).count(),
        })


class FollowersAPIView(APIView):
    """Get user's followers."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        followers = UserFollow.objects.filter(following=request.user)
        return Response({
            'followers': [{
                'id': f.follower.id,
                'username': f.follower.username,
                'avatar': f.follower.avatar.url if f.follower.avatar else None,
                'level': f.follower.current_level,
            } for f in followers]
        })


class FollowingAPIView(APIView):
    """Get users that the current user follows."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        following = UserFollow.objects.filter(follower=request.user)
        return Response({
            'following': [{
                'id': f.following.id,
                'username': f.following.username,
                'avatar': f.following.avatar.url if f.following.avatar else None,
                'level': f.following.current_level,
            } for f in following]
        })


class LeaderboardAPIView(APIView):
    """Get global leaderboard."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        limit = int(request.GET.get('limit', 100))
        users = User.objects.filter(privacy_mode='public').order_by('-total_xp')[:limit]
        return Response({
            'leaderboard': [{
                'rank': idx + 1,
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar.url if user.avatar else None,
                'total_xp': user.total_xp,
                'level': user.current_level,
                'streak': user.current_streak,
            } for idx, user in enumerate(users)]
        })


class FeedAPIView(APIView):
    """Get public activity feed."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        
        # Get recent completed tasks from public users
        week_ago = timezone.now() - timedelta(days=7)
        tasks = Task.objects.filter(
            user__privacy_mode='public',
            status='completed',
            completed_at__gte=week_ago
        ).select_related('user', 'category').order_by('-completed_at')[:50]
        
        return Response({
            'feed': [{
                'id': task.id,
                'user': {
                    'id': task.user.id,
                    'username': task.user.username,
                    'avatar': task.user.avatar.url if task.user.avatar else None,
                },
                'task': {
                    'title': task.title,
                    'category': task.category.name,
                    'xp_earned': task.awarded_xp,
                },
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            } for task in tasks]
        })

