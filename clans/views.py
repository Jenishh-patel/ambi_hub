"""
Clan Games views.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Clan, ClanMember


@login_required
def clans_list_view(request):
    """List all clans."""
    return render(request, 'clans/clans_list.html')


@login_required
def clan_detail_view(request, clan_id):
    """Clan detail page."""
    clan = get_object_or_404(Clan, id=clan_id)
    from .models import ClanMember
    member = ClanMember.objects.filter(clan=clan, user=request.user).first()
    is_leader = member and member.role in ['leader', 'admin'] if member else False
    return render(request, 'clans/clan_detail.html', {'clan': clan, 'is_leader': is_leader})


@login_required
def clan_dashboard_view(request, clan_id):
    """Clan dashboard."""
    clan = get_object_or_404(Clan, id=clan_id)
    return render(request, 'clans/clan_dashboard.html', {'clan': clan})


@login_required
def leader_dashboard_view(request, clan_id):
    """Leader dashboard for clan management."""
    clan = get_object_or_404(Clan, id=clan_id)
    from .models import ClanMember
    member = ClanMember.objects.filter(clan=clan, user=request.user).first()
    
    if not member or member.role not in ['leader', 'admin']:
        from django.contrib import messages
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('clan_detail', clan_id=clan_id)
    
    return render(request, 'clans/leader_dashboard.html', {'clan': clan, 'member': member})

