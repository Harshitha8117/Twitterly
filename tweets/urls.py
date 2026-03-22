from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tweet/<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('tweet/<int:tweet_id>/like/', views.like_toggle, name='like_toggle'),
    path('tweet/<int:tweet_id>/retweet/', views.retweet_toggle, name='retweet_toggle'),
    path('tweet/<int:tweet_id>/quote/', views.quote_tweet, name='quote_tweet'),
    path('tweet/<int:tweet_id>/delete/', views.delete_tweet, name='delete_tweet'),
    path('tweet/<int:tweet_id>/bookmark/', views.bookmark_toggle, name='bookmark_toggle'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('explore/', views.explore, name='explore'),
    path('hashtag/<str:tag>/', views.hashtag_tweets, name='hashtag_tweets'),
    path('tweet/<int:tweet_id>/status/', views.tweet_status, name='tweet_status'),
]
