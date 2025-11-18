"""
API views for adminpanel app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from clans.models import Clan
from solo.models import Task
from .models import GlobalChallenge, PlatformAnalytics

User = get_user_model()


@method_decorator(staff_member_required, name='dispatch')
class PlatformStatsAPIView(APIView):
    """Get platform-wide statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(
            last_activity_date__isnull=False
        ).count()
        total_tasks = Task.objects.filter(status='completed').count()
        total_xp = sum(user.total_xp for user in User.objects.all())
        total_clans = Clan.objects.count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'total_tasks_completed': total_tasks,
            'total_xp_earned': total_xp,
            'total_clans': total_clans,
        })


@method_decorator(staff_member_required, name='dispatch')
class UsersAPIView(APIView):
    """Manage users."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        users = User.objects.all().order_by('-total_xp')[:100]
        return Response({
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'total_xp': user.total_xp,
                'level': user.current_level,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
            } for user in users]
        })
    
    def post(self, request):
        user_id = request.data.get('user_id')
        action = request.data.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            if action == 'suspend':
                user.is_active = False
                user.save()
            elif action == 'activate':
                user.is_active = True
                user.save()
            
            return Response({'message': f'User {action}ed successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)


@method_decorator(staff_member_required, name='dispatch')
class ClansAPIView(APIView):
    """Manage clans."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        clans = Clan.objects.all().order_by('-created_at')
        return Response({
            'clans': [{
                'id': clan.id,
                'name': clan.name,
                'leader': clan.leader.username,
                'member_count': clan.get_member_count(),
                'visibility': clan.visibility,
                'created_at': clan.created_at.isoformat(),
            } for clan in clans]
        })


@method_decorator(staff_member_required, name='dispatch')
class GlobalChallengesAPIView(APIView):
    """Manage global challenges."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        challenges = GlobalChallenge.objects.all().order_by('-created_at')
        return Response({
            'challenges': [{
                'id': challenge.id,
                'title': challenge.title,
                'description': challenge.description,
                'target_xp': challenge.target_xp,
                'status': challenge.status,
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
            } for challenge in challenges]
        })
    
    def post(self, request):
        challenge = GlobalChallenge.objects.create(
            title=request.data.get('title'),
            description=request.data.get('description', ''),
            target_xp=int(request.data.get('target_xp', 10000)),
            reward_xp=int(request.data.get('reward_xp', 500)),
            start_date=request.data.get('start_date'),
            end_date=request.data.get('end_date'),
            created_by=request.user,
        )
        
        return Response({
            'id': challenge.id,
            'title': challenge.title,
        }, status=201)

