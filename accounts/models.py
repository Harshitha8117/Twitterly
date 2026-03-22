from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    bio = models.TextField(max_length=160, blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, default='')
    website = models.URLField(blank=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='following', blank=True
    )
    is_verified = models.BooleanField(default=False)
    is_warned = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    warning_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'@{self.username}'

    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()

    def is_following(self, user):
        return self.following.filter(pk=user.pk).exists()

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_avatar.png'

    def get_cover_photo_url(self):
        if self.cover_photo:
            return self.cover_photo.url
        return '/static/images/default_cover.png'
