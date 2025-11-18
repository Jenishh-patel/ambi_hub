"""
API views for clans app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    Clan, ClanMember, ClanJoinRequest,
    ClanChallenge, ClanProgress, ClanMessage
)
from solo.models import Task


class ClanAPIView(APIView):
    """List and create clans."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        visibility = request.GET.get('visibility', 'all')
        clans = Clan.objects.all()
        
        if visibility == 'public':
            clans = clans.filter(visibility='public')
        elif visibility == 'private':
            clans = clans.filter(visibility='private')
        
        return Response({
            'clans': [{
                'id': clan.id,
                'name': clan.name,
                'description': clan.description,
                'leader': {
                    'id': clan.leader.id,
                    'username': clan.leader.username,
                },
                'visibility': clan.visibility,
                'max_members': clan.max_members,
                'member_count': clan.get_member_count(),
                'icon': clan.icon,
                'created_at': clan.created_at.isoformat(),
            } for clan in clans]
        })
    
    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', '')
        visibility = request.data.get('visibility', 'public')
        max_members = int(request.data.get('max_members', 50))
        icon = request.data.get('icon', '🏆')
        
        clan = Clan.objects.create(
            name=name,
            description=description,
            leader=request.user,
            visibility=visibility,
            max_members=max_members,
            icon=icon
        )
        
        # Add creator as leader
        ClanMember.objects.create(
            clan=clan,
            user=request.user,
            role='leader'
        )
        
        return Response({
            'id': clan.id,
            'name': clan.name,
            'description': clan.description,
            'visibility': clan.visibility,
        }, status=status.HTTP_201_CREATED)


class ClanDetailAPIView(APIView):
    """Get, update, delete clan."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        is_member = ClanMember.objects.filter(clan=clan, user=request.user).exists()
        is_leader = ClanMember.objects.filter(
            clan=clan,
            user=request.user,
            role__in=['leader', 'admin']
        ).exists()
        
        return Response({
            'id': clan.id,
            'name': clan.name,
            'description': clan.description,
            'leader': {
                'id': clan.leader.id,
                'username': clan.leader.username,
            },
            'visibility': clan.visibility,
            'max_members': clan.max_members,
            'member_count': clan.get_member_count(),
            'icon': clan.icon,
            'is_member': is_member,
            'is_leader': is_leader,
            'created_at': clan.created_at.isoformat(),
        })
    
    def put(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        member = get_object_or_404(ClanMember, clan=clan, user=request.user)
        
        if member.role not in ['leader', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        clan.name = request.data.get('name', clan.name)
        clan.description = request.data.get('description', clan.description)
        clan.visibility = request.data.get('visibility', clan.visibility)
        clan.max_members = int(request.data.get('max_members', clan.max_members))
        clan.icon = request.data.get('icon', clan.icon)
        clan.save()
        
        return Response({
            'id': clan.id,
            'name': clan.name,
            'description': clan.description,
        })
    
    def delete(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        if clan.leader != request.user:
            return Response({'error': 'Only leader can delete clan'}, status=status.HTTP_403_FORBIDDEN)
        
        clan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JoinClanAPIView(APIView):
    """Join a clan."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        
        if ClanMember.objects.filter(clan=clan, user=request.user).exists():
            return Response({'error': 'Already a member'}, status=status.HTTP_400_BAD_REQUEST)
        
        if clan.is_full():
            return Response({'error': 'Clan is full'}, status=status.HTTP_400_BAD_REQUEST)
        
        if clan.visibility == 'private':
            # Create join request
            ClanJoinRequest.objects.get_or_create(
                clan=clan,
                user=request.user,
                defaults={'status': 'pending'}
            )
            return Response({'message': 'Join request sent'}, status=status.HTTP_201_CREATED)
        else:
            # Direct join
            ClanMember.objects.create(clan=clan, user=request.user)
            return Response({'message': 'Joined clan successfully'}, status=status.HTTP_201_CREATED)


class LeaveClanAPIView(APIView):
    """Leave a clan."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        member = get_object_or_404(ClanMember, clan=clan, user=request.user)
        
        if member.role == 'leader':
            return Response({'error': 'Leader cannot leave clan'}, status=status.HTTP_400_BAD_REQUEST)
        
        member.delete()
        return Response({'message': 'Left clan successfully'})


class ClanMembersAPIView(APIView):
    """Get clan members."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        members = ClanMember.objects.filter(clan=clan).select_related('user').order_by('-total_contribution_xp')
        
        return Response({
            'members': [{
                'id': member.user.id,
                'username': member.user.username,
                'avatar': member.user.avatar.url if member.user.avatar else None,
                'role': member.role,
                'total_contribution_xp': member.total_contribution_xp,
                'level': member.user.current_level,
                'joined_at': member.joined_at.isoformat(),
            } for member in members]
        })


class ClanChallengesAPIView(APIView):
    """Get and create clan challenges."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        challenges = ClanChallenge.objects.filter(clan=clan).order_by('-created_at')
        
        return Response({
            'challenges': [{
                'id': challenge.id,
                'title': challenge.title,
                'description': challenge.description,
                'target_xp': challenge.target_xp,
                'reward_xp': challenge.reward_xp,
                'status': challenge.status,
                'progress': challenge.get_progress(),
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
            } for challenge in challenges]
        })
    
    def post(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        member = get_object_or_404(ClanMember, clan=clan, user=request.user)
        
        if member.role not in ['leader', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        challenge = ClanChallenge.objects.create(
            clan=clan,
            created_by=request.user,
            title=request.data.get('title'),
            description=request.data.get('description', ''),
            target_xp=int(request.data.get('target_xp', 1000)),
            reward_xp=int(request.data.get('reward_xp', 100)),
            end_date=request.data.get('end_date'),
        )
        
        return Response({
            'id': challenge.id,
            'title': challenge.title,
            'target_xp': challenge.target_xp,
        }, status=status.HTTP_201_CREATED)


class ClanLeaderboardAPIView(APIView):
    """Get clan leaderboard."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        members = ClanMember.objects.filter(clan=clan).select_related('user').order_by('-total_contribution_xp')
        
        return Response({
            'leaderboard': [{
                'rank': idx + 1,
                'user': {
                    'id': member.user.id,
                    'username': member.user.username,
                    'avatar': member.user.avatar.url if member.user.avatar else None,
                },
                'contribution_xp': member.total_contribution_xp,
                'level': member.user.current_level,
            } for idx, member in enumerate(members)]
        })


class ClanMessagesAPIView(APIView):
    """Get and post clan messages."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        messages = ClanMessage.objects.filter(clan=clan).select_related('user').order_by('-created_at')[:50]
        
        return Response({
            'messages': [{
                'id': msg.id,
                'user': {
                    'id': msg.user.id,
                    'username': msg.user.username,
                    'avatar': msg.user.avatar.url if msg.user.avatar else None,
                },
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
            } for msg in messages]
        })
    
    def post(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        if not ClanMember.objects.filter(clan=clan, user=request.user).exists():
            return Response({'error': 'Not a member'}, status=status.HTTP_403_FORBIDDEN)
        
        message = ClanMessage.objects.create(
            clan=clan,
            user=request.user,
            content=request.data.get('content', '')
        )
        
        return Response({
            'id': message.id,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)


class ClanProgressAPIView(APIView):
    """Submit progress for clan challenge."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        if not ClanMember.objects.filter(clan=clan, user=request.user).exists():
            return Response({'error': 'Not a member'}, status=status.HTTP_403_FORBIDDEN)
        
        challenge_id = request.data.get('challenge_id')
        task_id = request.data.get('task_id')
        xp_contributed = int(request.data.get('xp_contributed', 0))
        notes = request.data.get('notes', '')
        
        challenge = get_object_or_404(ClanChallenge, id=challenge_id, clan=clan)
        task = get_object_or_404(Task, id=task_id, user=request.user) if task_id else None
        
        progress = ClanProgress.objects.create(
            challenge=challenge,
            user=request.user,
            task=task,
            xp_contributed=xp_contributed,
            notes=notes
        )
        
        # Update member contribution
        member = ClanMember.objects.get(clan=clan, user=request.user)
        member.total_contribution_xp += xp_contributed
        member.save()
        
        return Response({
            'id': progress.id,
            'xp_contributed': progress.xp_contributed,
        }, status=status.HTTP_201_CREATED)


class ClanJoinRequestsAPIView(APIView):
    """Get pending join requests for a clan."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, clan_id):
        clan = get_object_or_404(Clan, id=clan_id)
        member = get_object_or_404(ClanMember, clan=clan, user=request.user)
        
        if member.role not in ['leader', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        requests = ClanJoinRequest.objects.filter(
            clan=clan,
            status='pending'
        ).select_related('user').order_by('-created_at')
        
        return Response({
            'requests': [{
                'id': req.id,
                'user': {
                    'id': req.user.id,
                    'username': req.user.username,
                    'avatar': req.user.avatar.url if req.user.avatar else None,
                    'level': req.user.current_level,
                },
                'message': req.message,
                'created_at': req.created_at.isoformat(),
            } for req in requests]
        })


class ApproveJoinRequestAPIView(APIView):
    """Approve or reject a join request."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, clan_id, user_id):
        clan = get_object_or_404(Clan, id=clan_id)
        member = get_object_or_404(ClanMember, clan=clan, user=request.user)
        
        if member.role not in ['leader', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get('action', 'approve')
        join_request = get_object_or_404(
            ClanJoinRequest,
            clan=clan,
            user_id=user_id,
            status='pending'
        )
        
        if action == 'approve':
            if clan.is_full():
                return Response({'error': 'Clan is full'}, status=status.HTTP_400_BAD_REQUEST)
            
            ClanMember.objects.create(clan=clan, user=join_request.user)
            join_request.status = 'approved'
            join_request.reviewed_by = request.user
            join_request.reviewed_at = timezone.now()
            join_request.save()
            
            return Response({'message': 'Join request approved'})
        else:
            join_request.status = 'rejected'
            join_request.reviewed_by = request.user
            join_request.reviewed_at = timezone.now()
            join_request.save()
            
            return Response({'message': 'Join request rejected'})


class RemoveMemberAPIView(APIView):
    """Remove a member from clan."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, clan_id, user_id):
        clan = get_object_or_404(Clan, id=clan_id)
        member = get_object_or_404(ClanMember, clan=clan, user=request.user)
        
        if member.role not in ['leader', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        target_member = get_object_or_404(ClanMember, clan=clan, user_id=user_id)
        
        if target_member.role == 'leader':
            return Response({'error': 'Cannot remove leader'}, status=status.HTTP_400_BAD_REQUEST)
        
        target_member.delete()
        return Response({'message': 'Member removed'})


class PromoteMemberAPIView(APIView):
    """Promote a member to admin."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, clan_id, user_id):
        clan = get_object_or_404(Clan, id=clan_id)
        member = get_object_or_404(ClanMember, clan=clan, user=request.user)
        
        if member.role != 'leader':
            return Response({'error': 'Only leader can promote members'}, status=status.HTTP_403_FORBIDDEN)
        
        target_member = get_object_or_404(ClanMember, clan=clan, user_id=user_id)
        target_member.role = 'admin'
        target_member.save()
        
        return Response({'message': 'Member promoted to admin'})

