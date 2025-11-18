"""
Main URL configuration for ambitioushub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('solo.urls')),
    path('clans/', include('clans.urls')),
    path('achievements/', include('achievements.urls')),
    path('analytics/', include('analytics.urls')),
    path('adminpanel/', include('adminpanel.urls')),
    path('workout/', include('workout.urls')),
    path('api/accounts/', include('accounts.api_urls')),
    path('api/solo/', include('solo.api_urls')),
    path('api/clans/', include('clans.api_urls')),
    path('api/achievements/', include('achievements.api_urls')),
    path('api/analytics/', include('analytics.api_urls')),
    path('api/workout/', include('workout.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

