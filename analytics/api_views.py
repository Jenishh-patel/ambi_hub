"""
API views for analytics app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
from solo.models import Task, DailySummary
from .models import UserReport


class DailyAnalyticsAPIView(APIView):
    """Get daily analytics data."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        date_str = request.GET.get('date')
        if date_str:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        tasks = Task.objects.filter(
            user=request.user,
            status='completed',
            completed_at__date=date
        )
        
        categories = {}
        for task in tasks:
            cat_name = task.category.name
            if cat_name not in categories:
                categories[cat_name] = {'count': 0, 'xp': 0}
            categories[cat_name]['count'] += 1
            categories[cat_name]['xp'] += task.awarded_xp
        
        return Response({
            'date': date.isoformat(),
            'total_tasks': tasks.count(),
            'total_xp': sum(task.awarded_xp for task in tasks),
            'categories': categories,
        })


class WeeklyAnalyticsAPIView(APIView):
    """Get weekly analytics data."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        
        tasks = Task.objects.filter(
            user=request.user,
            status='completed',
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        )
        
        # Group by day
        daily_data = {}
        for task in tasks:
            day = task.completed_at.date().isoformat()
            if day not in daily_data:
                daily_data[day] = {'tasks': 0, 'xp': 0}
            daily_data[day]['tasks'] += 1
            daily_data[day]['xp'] += task.awarded_xp
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_tasks': tasks.count(),
            'total_xp': sum(task.awarded_xp for task in tasks),
            'daily_data': daily_data,
        })


class MonthlyAnalyticsAPIView(APIView):
    """Get monthly analytics data."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        tasks = Task.objects.filter(
            user=request.user,
            status='completed',
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        )
        
        # Group by week
        weekly_data = {}
        for task in tasks:
            week_start = task.completed_at.date() - timedelta(days=task.completed_at.date().weekday())
            week_key = week_start.isoformat()
            if week_key not in weekly_data:
                weekly_data[week_key] = {'tasks': 0, 'xp': 0}
            weekly_data[week_key]['tasks'] += 1
            weekly_data[week_key]['xp'] += task.awarded_xp
        
        return Response({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_tasks': tasks.count(),
            'total_xp': sum(task.awarded_xp for task in tasks),
            'weekly_data': weekly_data,
        })


class XPTimelineAPIView(APIView):
    """Get XP timeline data for charts."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        summaries = DailySummary.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        labels = []
        xp_data = []
        cumulative_xp = 0
        
        for summary in summaries:
            labels.append(summary.date.isoformat())
            cumulative_xp += summary.xp_earned
            xp_data.append(cumulative_xp)
        
        return Response({
            'labels': labels,
            'xp_data': xp_data,
        })


class CategoryTrendsAPIView(APIView):
    """Get category-wise trends."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        tasks = Task.objects.filter(
            user=request.user,
            status='completed',
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        ).select_related('category')
        
        category_data = {}
        for task in tasks:
            cat_name = task.category.name
            if cat_name not in category_data:
                category_data[cat_name] = {
                    'total_tasks': 0,
                    'total_xp': 0,
                    'color': task.category.color,
                }
            category_data[cat_name]['total_tasks'] += 1
            category_data[cat_name]['total_xp'] += task.awarded_xp
        
        return Response({
            'categories': category_data,
        })


class ExportPDFAPIView(APIView):
    """Export analytics report as PDF."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        report_type = request.data.get('report_type', 'weekly')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        # Create report record
        report = UserReport.objects.create(
            user=request.user,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
        )
        
        # TODO: Implement actual PDF generation
        # For now, return a placeholder response
        return Response({
            'report_id': report.id,
            'message': 'PDF export functionality - to be implemented with reportlab or weasyprint',
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date,
        })

