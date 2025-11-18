"""
Management command to initialize default exercises.
"""
from django.core.management.base import BaseCommand
from workout.models import Exercise


class Command(BaseCommand):
    help = 'Initialize default exercises for Workout module'

    def handle(self, *args, **options):
        default_exercises = [
            # Push exercises
            {'name': 'Bench Press', 'category': 'push'},
            {'name': 'Shoulder Press', 'category': 'push'},
            {'name': 'Incline Bench Press', 'category': 'push'},
            {'name': 'Dumbbell Press', 'category': 'push'},
            {'name': 'Push-ups', 'category': 'push'},
            {'name': 'Dips', 'category': 'push'},
            {'name': 'Tricep Extensions', 'category': 'push'},
            
            # Pull exercises
            {'name': 'Deadlift', 'category': 'pull'},
            {'name': 'Pull-ups', 'category': 'pull'},
            {'name': 'Barbell Rows', 'category': 'pull'},
            {'name': 'Lat Pulldown', 'category': 'pull'},
            {'name': 'Bicep Curls', 'category': 'pull'},
            {'name': 'Cable Rows', 'category': 'pull'},
            
            # Legs exercises
            {'name': 'Squat', 'category': 'legs'},
            {'name': 'Leg Press', 'category': 'legs'},
            {'name': 'Romanian Deadlift', 'category': 'legs'},
            {'name': 'Lunges', 'category': 'legs'},
            {'name': 'Leg Curls', 'category': 'legs'},
            {'name': 'Leg Extensions', 'category': 'legs'},
            {'name': 'Calf Raises', 'category': 'legs'},
            
            # Core exercises
            {'name': 'Plank', 'category': 'core'},
            {'name': 'Crunches', 'category': 'core'},
            {'name': 'Russian Twists', 'category': 'core'},
            {'name': 'Leg Raises', 'category': 'core'},
            
            # Cardio
            {'name': 'Running', 'category': 'cardio'},
            {'name': 'Cycling', 'category': 'cardio'},
            {'name': 'Rowing', 'category': 'cardio'},
        ]
        
        created_count = 0
        for ex_data in default_exercises:
            exercise, created = Exercise.objects.get_or_create(
                name=ex_data['name'],
                category=ex_data['category'],
                user=None,  # Global exercises
                defaults={
                    'is_default': True,
                    **ex_data
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created exercise: {exercise.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Exercise already exists: {exercise.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully initialized {created_count} default exercises.')
        )

