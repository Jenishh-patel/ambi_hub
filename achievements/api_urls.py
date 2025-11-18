"""
API URL routing for achievements app.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('badges/', api_views.BadgesAPIView.as_view(), name='api_badges'),
    path('milestones/', api_views.MilestonesAPIView.as_view(), name='api_milestones'),
    path('certificate/<int:milestone_id>/', api_views.CertificateAPIView.as_view(), name='api_certificate'),
]

