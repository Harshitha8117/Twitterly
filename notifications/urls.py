from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_view, name='notifications'),
    path('<int:notif_id>/read/', views.mark_read, name='mark_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
]
