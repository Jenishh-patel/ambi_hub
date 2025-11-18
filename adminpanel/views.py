"""
Admin panel views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


@login_required
@staff_member_required
def admin_panel_view(request):
    """Admin panel page."""
    return render(request, 'adminpanel/admin_panel.html')

