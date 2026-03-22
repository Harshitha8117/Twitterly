from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('tweets.urls')),
    path('accounts/', include('accounts.urls')),
    path('notifications/', include('notifications.urls')),
    path('admin-portal/', include('admin_portal.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
