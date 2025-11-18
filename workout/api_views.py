"""
API views for workout app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Max, Q
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import Exercise, WorkoutSession, SetEntry, PersonalRecord
import json


class ExerciseAPIView(APIView):
    """List and create exercises."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get default exercises and user's custom exercises
        exercises = Exercise.objects.filter(
            Q(is_default=True) | Q(user=request.user)
        ).distinct().order_by('category', 'name')
        
        return Response({
            'exercises': [{
                'id': ex.id,
                'name': ex.name,
                'category': ex.category,
                'is_default': ex.is_default,
                'user': ex.user.username if ex.user else None,
            } for ex in exercises]
        })
    
    def post(self, request):
        name = request.data.get('name')
        category = request.data.get('category', 'custom')
        
        exercise = Exercise.objects.create(
            name=name,
            category=category,
            user=request.user,
            is_default=False
        )
        
        return Response({
            'id': exercise.id,
            'name': exercise.name,
            'category': exercise.category,
        }, status=status.HTTP_201_CREATED)


class ExerciseDetailAPIView(APIView):
    """Get, update, delete exercise."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id)
        if not exercise.is_default and exercise.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'id': exercise.id,
            'name': exercise.name,
            'category': exercise.category,
            'is_default': exercise.is_default,
        })
    
    def put(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
        exercise.name = request.data.get('name', exercise.name)
        exercise.category = request.data.get('category', exercise.category)
        exercise.save()
        
        return Response({
            'id': exercise.id,
            'name': exercise.name,
            'category': exercise.category,
        })
    
    def delete(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
        exercise.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkoutSessionAPIView(APIView):
    """List workout sessions."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        month = request.GET.get('month')
        year = request.GET.get('year')
        
        sessions = WorkoutSession.objects.filter(user=request.user)
        
        if month and year:
            sessions = sessions.filter(date__year=year, date__month=month)
        
        sessions = sessions.select_related('user').prefetch_related('sets__exercise').order_by('-date')
        
        return Response({
            'sessions': [{
                'id': session.id,
                'date': session.date.isoformat(),
                'total_volume': session.total_volume,
                'notes': session.notes,
                'sets_count': session.sets.count(),
                'exercises': list(session.sets.values('exercise__name').distinct()),
            } for session in sessions]
        })


class WorkoutSessionDetailAPIView(APIView):
    """Get workout session details with all sets."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        sets = session.sets.select_related('exercise').order_by('exercise__name', 'set_number')
        
        return Response({
            'id': session.id,
            'date': session.date.isoformat(),
            'total_volume': session.total_volume,
            'notes': session.notes,
            'sets': [{
                'id': s.id,
                'exercise': {
                    'id': s.exercise.id,
                    'name': s.exercise.name,
                    'category': s.exercise.category,
                },
                'reps': s.reps,
                'weight': s.weight,
                'rpe': s.rpe,
                'volume': s.volume,
                'set_number': s.set_number,
            } for s in sets]
        })


class LogSessionAPIView(APIView):
    """Log a new workout session with sets."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        date_str = request.data.get('date')
        notes = request.data.get('notes', '')
        sets_data = request.data.get('sets', [])
        
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        # Create or get session
        session, created = WorkoutSession.objects.get_or_create(
            user=request.user,
            date=date,
            defaults={'notes': notes}
        )
        
        if not created:
            session.notes = notes
            session.save()
        
        # Create set entries
        created_sets = []
        for set_data in sets_data:
            exercise = get_object_or_404(Exercise, id=set_data['exercise_id'])
            # Validate exercise category matches if category was provided
            set_entry = SetEntry.objects.create(
                session=session,
                exercise=exercise,
                reps=int(set_data['reps']),
                weight=float(set_data['weight']),
                rpe=int(set_data.get('rpe')) if set_data.get('rpe') else None,
                set_number=int(set_data.get('set_number', 1))
            )
            created_sets.append({
                'id': set_entry.id,
                'exercise': exercise.name,
                'category': exercise.category,
                'reps': set_entry.reps,
                'weight': set_entry.weight,
                'volume': set_entry.volume,
            })
        
        # Recalculate total volume
        session.calculate_total_volume()
        
        return Response({
            'session': {
                'id': session.id,
                'date': session.date.isoformat(),
                'total_volume': session.total_volume,
            },
            'sets': created_sets,
        }, status=status.HTTP_201_CREATED)


class WorkoutAnalyticsAPIView(APIView):
    """Get analytics data for charts."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        days = int(request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        sessions = WorkoutSession.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).prefetch_related('sets__exercise')
        
        # Weight progression (max weight per exercise per week)
        weight_progression = {}
        volume_progression = {}
        weekly_load = {}
        exercise_names = set()
        
        for session in sessions:
            week_start = session.date - timedelta(days=session.date.weekday())
            week_key = week_start.isoformat()
            
            if week_key not in weekly_load:
                weekly_load[week_key] = 0
            
            weekly_load[week_key] += session.total_volume
            
            for set_entry in session.sets.all():
                ex_name = set_entry.exercise.name
                exercise_names.add(ex_name)
                
                if ex_name not in weight_progression:
                    weight_progression[ex_name] = {}
                if ex_name not in volume_progression:
                    volume_progression[ex_name] = {}
                
                date_key = session.date.isoformat()
                if date_key not in weight_progression[ex_name]:
                    weight_progression[ex_name][date_key] = set_entry.weight
                else:
                    weight_progression[ex_name][date_key] = max(
                        weight_progression[ex_name][date_key],
                        set_entry.weight
                    )
                
                if date_key not in volume_progression[ex_name]:
                    volume_progression[ex_name][date_key] = 0
                volume_progression[ex_name][date_key] += set_entry.volume
        
        # Personal Records
        prs = PersonalRecord.objects.filter(user=request.user).select_related('exercise')
        
        # Training frequency heatmap (monthly)
        heatmap_data = {}
        for session in sessions:
            date_key = session.date.isoformat()
            heatmap_data[date_key] = heatmap_data.get(date_key, 0) + 1
        
        return Response({
            'weight_progression': weight_progression,
            'volume_progression': volume_progression,
            'weekly_load': weekly_load,
            'personal_records': [{
                'exercise': pr.exercise.name,
                'max_weight': pr.max_weight,
                'date_achieved': pr.date_achieved.isoformat(),
            } for pr in prs],
            'heatmap_data': heatmap_data,
            'exercises': list(exercise_names),
        })


class PersonalRecordsAPIView(APIView):
    """Get personal records."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        prs = PersonalRecord.objects.filter(user=request.user).select_related('exercise').order_by('-max_weight')
        
        return Response({
            'personal_records': [{
                'id': pr.id,
                'exercise': {
                    'id': pr.exercise.id,
                    'name': pr.exercise.name,
                    'category': pr.exercise.category,
                },
                'max_weight': pr.max_weight,
                'date_achieved': pr.date_achieved.isoformat(),
            } for pr in prs]
        })


class ExportWorkoutReportAPIView(APIView):
    """Export monthly workout report as Excel."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill
            from openpyxl.utils import get_column_letter
        except ImportError:
            return Response(
                {'error': 'openpyxl is required. Install with: pip install openpyxl'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        month = int(request.GET.get('month', timezone.now().month))
        year = int(request.GET.get('year', timezone.now().year))
        
        sessions = WorkoutSession.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        ).prefetch_related('sets__exercise').order_by('date')
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Workout Report {year}-{month:02d}"
        
        # Header style
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        # Summary sheet
        summary_ws = wb.create_sheet("Summary")
        
        # Summary headers
        summary_ws['A1'] = 'Metric'
        summary_ws['B1'] = 'Value'
        summary_ws['A1'].fill = header_fill
        summary_ws['A1'].font = header_font
        summary_ws['B1'].fill = header_fill
        summary_ws['B1'].font = header_font
        
        total_volume = sum(s.total_volume for s in sessions)
        total_sessions = sessions.count()
        total_sets = sum(s.sets.count() for s in sessions)
        
        summary_data = [
            ['Total Sessions', total_sessions],
            ['Total Sets', total_sets],
            ['Total Volume (kg)', total_volume],
            ['Average Volume per Session', total_volume / total_sessions if total_sessions > 0 else 0],
        ]
        
        for idx, (metric, value) in enumerate(summary_data, start=2):
            summary_ws[f'A{idx}'] = metric
            summary_ws[f'B{idx}'] = value
        
        # Main data sheet headers
        headers = ['Date', 'Category', 'Exercise', 'Set #', 'Reps', 'Weight (kg)', 'Volume (kg)', 'RPE', 'Session Volume']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
        
        # Write data
        row = 2
        for session in sessions:
            session_volume = session.total_volume
            sets_list = list(session.sets.select_related('exercise').order_by('exercise__name', 'set_number'))
            
            for idx, set_entry in enumerate(sets_list):
                ws.cell(row=row, column=1, value=session.date.strftime('%Y-%m-%d'))
                ws.cell(row=row, column=2, value=set_entry.exercise.category)
                ws.cell(row=row, column=3, value=set_entry.exercise.name)
                ws.cell(row=row, column=4, value=set_entry.set_number)
                ws.cell(row=row, column=5, value=set_entry.reps)
                ws.cell(row=row, column=6, value=set_entry.weight)
                ws.cell(row=row, column=7, value=set_entry.volume)
                ws.cell(row=row, column=8, value=set_entry.rpe if set_entry.rpe else '')
                ws.cell(row=row, column=9, value=session_volume if idx == 0 else '')
                row += 1
        
        # Auto-adjust column widths
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 15
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"workout_report_{year}_{month:02d}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        wb.save(response)
        return response

