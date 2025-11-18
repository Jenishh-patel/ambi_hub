"""
API URL routing for analytics app.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('daily/', api_views.DailyAnalyticsAPIView.as_view(), name='api_daily_analytics'),
    path('weekly/', api_views.WeeklyAnalyticsAPIView.as_view(), name='api_weekly_analytics'),
    path('monthly/', api_views.MonthlyAnalyticsAPIView.as_view(), name='api_monthly_analytics'),
    path('xp-timeline/', api_views.XPTimelineAPIView.as_view(), name='api_xp_timeline'),
    path('category-trends/', api_views.CategoryTrendsAPIView.as_view(), name='api_category_trends'),
    path('export-pdf/', api_views.ExportPDFAPIView.as_view(), name='api_export_pdf'),
]

