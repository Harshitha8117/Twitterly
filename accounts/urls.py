from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('search/', views.search_users, name='search_users'),
    path('<str:username>/', views.profile_view, name='profile'),
    path('<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('<str:username>/following/', views.following_list, name='following_list'),
]
