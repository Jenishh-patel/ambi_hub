"""
API URL routing for solo app.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('categories/', api_views.CategoryAPIView.as_view(), name='api_categories'),
    path('categories/<int:category_id>/', api_views.CategoryDetailAPIView.as_view(), name='api_category_detail'),
    path('tasks/', api_views.TaskAPIView.as_view(), name='api_tasks'),
    path('tasks/<int:task_id>/', api_views.TaskDetailAPIView.as_view(), name='api_task_detail'),
    path('tasks/<int:task_id>/complete/', api_views.CompleteTaskAPIView.as_view(), name='api_complete_task'),
    path('daily-summary/', api_views.DailySummaryAPIView.as_view(), name='api_daily_summary'),
    path('motivational-quote/', api_views.MotivationalQuoteAPIView.as_view(), name='api_motivational_quote'),
]

