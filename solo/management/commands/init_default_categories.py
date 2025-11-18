"""
Management command to initialize default categories.
"""
from django.core.management.base import BaseCommand
from solo.models import Category


class Command(BaseCommand):
    help = 'Initialize default categories for Solo Leveling'

    def handle(self, *args, **options):
        default_categories = [
            {
                'name': 'Coding',
                'category_type': 'coding',
                'icon': '💻',
                'color': '#3B82F6',
                'xp_multiplier': 1.2,
            },
            {
                'name': 'Gym',
                'category_type': 'gym',
                'icon': '💪',
                'color': '#EF4444',
                'xp_multiplier': 1.3,
            },
            {
                'name': 'Academics',
                'category_type': 'academics',
                'icon': '📚',
                'color': '#10B981',
                'xp_multiplier': 1.1,
            },
            {
                'name': 'Content Creation',
                'category_type': 'content',
                'icon': '🎬',
                'color': '#8B5CF6',
                'xp_multiplier': 1.15,
            },
            {
                'name': 'Reading',
                'category_type': 'reading',
                'icon': '📖',
                'color': '#F59E0B',
                'xp_multiplier': 1.0,
            },
            {
                'name': 'Habits',
                'category_type': 'habits',
                'icon': '✅',
                'color': '#06B6D4',
                'xp_multiplier': 1.0,
            },
        ]
        
        created_count = 0
        for cat_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                category_type=cat_data['category_type'],
                user=None,  # Global categories
                defaults=cat_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully initialized {created_count} default categories.')
        )

