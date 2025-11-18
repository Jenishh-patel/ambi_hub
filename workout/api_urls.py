"""
API URL routing for workout app.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('exercises/', api_views.ExerciseAPIView.as_view(), name='api_workout_exercises'),
    path('exercises/<int:exercise_id>/', api_views.ExerciseDetailAPIView.as_view(), name='api_workout_exercise_detail'),
    path('sessions/', api_views.WorkoutSessionAPIView.as_view(), name='api_workout_sessions'),
    path('sessions/<int:session_id>/', api_views.WorkoutSessionDetailAPIView.as_view(), name='api_workout_session_detail'),
    path('log-session/', api_views.LogSessionAPIView.as_view(), name='api_workout_log_session'),
    path('analytics/', api_views.WorkoutAnalyticsAPIView.as_view(), name='api_workout_analytics'),
    path('personal-records/', api_views.PersonalRecordsAPIView.as_view(), name='api_workout_personal_records'),
    path('export-report/', api_views.ExportWorkoutReportAPIView.as_view(), name='api_workout_export_report'),
]

