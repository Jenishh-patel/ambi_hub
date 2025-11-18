"""
Management command to initialize default badges.
"""
from django.core.management.base import BaseCommand
from achievements.models import Badge, Milestone


class Command(BaseCommand):
    help = 'Initialize default badges and milestones'

    def handle(self, *args, **options):
        default_badges = [
            {
                'name': 'First Steps',
                'description': 'Complete your first task',
                'icon': '🌱',
                'rarity': 'common',
                'xp_reward': 50,
                'condition_type': 'tasks_completed',
                'condition_value': 1,
            },
            {
                'name': 'Getting Started',
                'description': 'Complete 10 tasks',
                'icon': '⭐',
                'rarity': 'common',
                'xp_reward': 100,
                'condition_type': 'tasks_completed',
                'condition_value': 10,
            },
            {
                'name': 'Productive',
                'description': 'Complete 50 tasks',
                'icon': '🔥',
                'rarity': 'uncommon',
                'xp_reward': 250,
                'condition_type': 'tasks_completed',
                'condition_value': 50,
            },
            {
                'name': 'Dedicated',
                'description': 'Complete 100 tasks',
                'icon': '💎',
                'rarity': 'rare',
                'xp_reward': 500,
                'condition_type': 'tasks_completed',
                'condition_value': 100,
            },
            {
                'name': 'Level 5',
                'description': 'Reach level 5',
                'icon': '🎯',
                'rarity': 'common',
                'xp_reward': 100,
                'condition_type': 'level_reached',
                'condition_value': 5,
            },
            {
                'name': 'Level 10',
                'description': 'Reach level 10',
                'icon': '🏆',
                'rarity': 'uncommon',
                'xp_reward': 250,
                'condition_type': 'level_reached',
                'condition_value': 10,
            },
            {
                'name': 'Week Warrior',
                'description': 'Maintain a 7-day streak',
                'icon': '⚡',
                'rarity': 'uncommon',
                'xp_reward': 200,
                'condition_type': 'streak_days',
                'condition_value': 7,
            },
            {
                'name': 'Month Master',
                'description': 'Maintain a 30-day streak',
                'icon': '👑',
                'rarity': 'epic',
                'xp_reward': 1000,
                'condition_type': 'streak_days',
                'condition_value': 30,
            },
        ]
        
        created_badges = 0
        for badge_data in default_badges:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_badges += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created badge: {badge.name}')
                )
        
        default_milestones = [
            {
                'name': 'Level 5 Milestone',
                'description': 'Reached level 5',
                'milestone_type': 'level',
                'milestone_value': 5,
                'celebration_message': 'Congratulations on reaching Level 5! You\'re making great progress!',
            },
            {
                'name': 'Level 10 Milestone',
                'description': 'Reached level 10',
                'milestone_type': 'level',
                'milestone_value': 10,
                'celebration_message': 'Amazing! You\'ve reached Level 10! Keep up the excellent work!',
            },
            {
                'name': '1000 XP Milestone',
                'description': 'Earned 1000 total XP',
                'milestone_type': 'xp',
                'milestone_value': 1000,
                'celebration_message': 'Incredible! You\'ve earned 1000 XP! You\'re on fire!',
            },
        ]
        
        created_milestones = 0
        for milestone_data in default_milestones:
            milestone, created = Milestone.objects.get_or_create(
                name=milestone_data['name'],
                defaults=milestone_data
            )
            if created:
                created_milestones += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created milestone: {milestone.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully initialized {created_badges} badges and {created_milestones} milestones.'
            )
        )

