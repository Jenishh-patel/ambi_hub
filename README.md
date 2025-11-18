# Ambitious Hub - Gamified Productivity Platform

A complete full-stack web application for tracking productivity through gamification, featuring Solo Leveling and Clan Games modes.

## Features

### Core Features
- **User Authentication**: Register, login, logout, password reset, profile management
- **Theme System**: Dark (neon) and Light (minimal) themes with smooth transitions
- **Dashboard**: XP bar, level display, streak tracking, daily summary, motivational quotes

### Solo Leveling
- Predefined categories (Coding, Gym, Academics, Content Creation, Reading, Habits) + custom categories
- Add/Edit/Delete tasks with timers, gym reps/weights, coding hours
- Optional proof upload
- XP & level calculation system
- Badges & rarity tiers
- Milestone celebrations
- Shareable certificates

### Clan Games
- Create/join clans (public/private)
- Clan dashboard and member management
- Submit progress for challenges
- Member comparison and leaderboards
- Clan challenges
- Simple clan chat/comment board

### Achievements & Reports
- Badge system with rarity tiers
- Milestone tracking
- PDF export (demo implementation)
- Personal analytics
- Category-wise trends

### Social Features
- Follow/unfollow users
- Public activity feed
- Global leaderboards

### Admin Features
- Clan admin: edit clan, approve join requests, manage members, create challenges
- Platform super-admin: manage users/clans, suspend accounts, create global challenges, analytics

## Tech Stack

- **Backend**: Django 4.2+ with modular apps
- **Frontend**: HTML/CSS/Vanilla JavaScript (no frameworks)
- **Database**: SQLite (default, can switch to MySQL)
- **Charts**: Chart.js
- **API**: Django REST Framework (optional, used for API endpoints)

## Project Structure

```
ambitioushub/
├── ambitioushub/          # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── accounts/               # User accounts app
├── solo/                  # Solo Leveling app
├── clans/                 # Clan Games app
├── achievements/          # Achievements & badges app
├── analytics/             # Analytics & reports app
├── adminpanel/            # Admin panel app
├── frontend/              # Frontend templates and static files
│   ├── templates/
│   └── static/
│       ├── css/
│       └── js/
├── manage.py
└── requirements.txt
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 5. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Database Models

### Accounts
- `User`: Extended user model with XP, level, streak
- `UserFollow`: Follow relationships

### Solo
- `Category`: Task categories (predefined + custom)
- `Task`: Individual tasks with XP calculation
- `DailySummary`: Daily activity summaries

### Clans
- `Clan`: Clan/group entities
- `ClanMember`: Membership with roles
- `ClanJoinRequest`: Join requests for private clans
- `ClanChallenge`: Clan challenges
- `ClanProgress`: Member progress submissions
- `ClanMessage`: Clan chat messages

### Achievements
- `Badge`: Badge definitions
- `UserBadge`: User badge achievements
- `Milestone`: Milestone definitions
- `UserMilestone`: User milestone achievements

### Analytics
- `UserReport`: Generated user reports

### Admin Panel
- `GlobalChallenge`: Platform-wide challenges
- `PlatformAnalytics`: Platform analytics snapshots

## API Endpoints

### Accounts
- `GET /api/accounts/profile/` - Get user profile
- `GET /api/accounts/dashboard-stats/` - Get dashboard statistics
- `GET /api/accounts/leaderboard/` - Get global leaderboard
- `GET /api/accounts/feed/` - Get public activity feed

### Solo
- `GET /api/solo/categories/` - List categories
- `POST /api/solo/categories/` - Create category
- `GET /api/solo/tasks/` - List tasks
- `POST /api/solo/tasks/` - Create task
- `POST /api/solo/tasks/{id}/complete/` - Complete task
- `GET /api/solo/daily-summary/` - Get daily summary
- `GET /api/solo/motivational-quote/` - Get motivational quote

### Clans
- `GET /api/clans/` - List clans
- `POST /api/clans/` - Create clan
- `GET /api/clans/{id}/` - Get clan details
- `POST /api/clans/{id}/join/` - Join clan
- `GET /api/clans/{id}/members/` - Get clan members
- `GET /api/clans/{id}/challenges/` - Get clan challenges
- `GET /api/clans/{id}/leaderboard/` - Get clan leaderboard
- `GET /api/clans/{id}/messages/` - Get clan messages
- `POST /api/clans/{id}/messages/` - Send clan message

### Achievements
- `GET /api/achievements/badges/` - Get user badges
- `GET /api/achievements/milestones/` - Get user milestones
- `GET /api/achievements/certificate/{id}/` - Get milestone certificate

### Analytics
- `GET /api/analytics/daily/` - Get daily analytics
- `GET /api/analytics/weekly/` - Get weekly analytics
- `GET /api/analytics/monthly/` - Get monthly analytics
- `GET /api/analytics/xp-timeline/` - Get XP timeline data
- `GET /api/analytics/category-trends/` - Get category trends
- `POST /api/analytics/export-pdf/` - Export PDF report

### Admin Panel
- `GET /api/adminpanel/platform-stats/` - Get platform statistics
- `GET /api/adminpanel/users/` - Get users
- `POST /api/adminpanel/users/` - Manage users (suspend/activate)
- `GET /api/adminpanel/clans/` - Get clans
- `GET /api/adminpanel/global-challenges/` - Get global challenges
- `POST /api/adminpanel/global-challenges/` - Create global challenge

## Configuration

### XP and Level Settings

Edit `ambitioushub/settings.py`:

```python
XP_PER_LEVEL = 1000  # Base XP needed per level
XP_MULTIPLIER = 1.2  # XP multiplier per level
```

### Database

Default is SQLite. To use MySQL, update `DATABASES` in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ambitioushub',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Extending Features

### Adding New Badge Types

1. Add badge condition in `achievements/models.py`
2. Update `check_badges()` in `achievements/utils.py`
3. Create badge via admin or migration

### Adding New Task Types

1. Add fields to `Task` model in `solo/models.py`
2. Update `calculate_xp()` method
3. Update frontend form in `solo_leveling.html`

### Customizing Themes

Edit `frontend/static/css/theme.css` to modify color schemes and effects.

### PDF Export Implementation

The PDF export endpoint is a placeholder. To implement:

1. Install `reportlab` or `weasyprint`:
   ```bash
   pip install reportlab
   ```

2. Update `analytics/api_views.py` `ExportPDFAPIView` to generate actual PDFs

## Development Notes

- All API endpoints require authentication (except registration/login)
- CSRF tokens are required for POST/PUT/DELETE requests
- Theme preference is stored per user
- XP calculations happen automatically when tasks are completed
- Badges and milestones are checked automatically

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, please refer to the Django documentation or create an issue in the project repository.

