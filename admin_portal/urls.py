from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('login/', views.admin_login_view, name='admin_login'),
    path('flagged/', views.flagged_content, name='admin_flagged'),
    path('flagged/<int:report_id>/', views.report_detail, name='admin_report_detail'),
    path('users/', views.user_management, name='admin_users'),
    path('users/<int:user_id>/', views.user_detail, name='admin_user_detail'),
    path('users/<int:user_id>/toggle-block/', views.toggle_block_user, name='admin_toggle_block'),
]
