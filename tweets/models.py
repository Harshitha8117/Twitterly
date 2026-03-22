from django.db import models
from django.conf import settings
from django.utils import timezone
import re


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'#{self.name}'


class Tweet(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tweets')
    content = models.TextField(max_length=280)
    image = models.ImageField(upload_to='tweet_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Retweet fields
    is_retweet = models.BooleanField(default=False)
    original_tweet = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='retweets')
    quote_content = models.TextField(max_length=280, blank=True, default='')

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    # ML Detection fields
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(
        max_length=20,
        choices=[('hate_speech', 'Hate Speech'), ('cyberbullying', 'Cyberbullying'), ('normal', 'Normal')],
        default='normal'
    )
    flag_confidence = models.FloatField(default=0.0)

    # Hashtags
    hashtags = models.ManyToManyField(Hashtag, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'@{self.author.username}: {self.content[:50]}'

    def get_likes_count(self):
        return self.likes.count()

    def get_retweets_count(self):
        return Tweet.objects.filter(original_tweet=self, is_deleted=False).count()

    def get_comments_count(self):
        return self.comments.filter(is_deleted=False).count()

    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()

    def is_retweeted_by(self, user):
        return Tweet.objects.filter(original_tweet=self, author=user, is_retweet=True, is_deleted=False).exists()

    def is_bookmarked_by(self, user):
        return self.bookmarks.filter(user=user).exists()

    def extract_hashtags(self):
        return re.findall(r'#(\w+)', self.content)

    def save_hashtags(self):
        tags = self.extract_hashtags()
        for tag in tags:
            hashtag, _ = Hashtag.objects.get_or_create(name=tag.lower())
            self.hashtags.add(hashtag)

    def get_flag_reason_display_name(self):
        return self.flag_reason.replace('_', ' ').title()


class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=20, default='normal')
    flag_confidence = models.FloatField(default=0.0)

    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'@{self.author.username} on tweet {self.tweet.id}: {self.content[:40]}'

    def get_flag_reason_display_name(self):
        return self.flag_reason.replace('_', ' ').title()


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f'@{self.user.username} likes tweet {self.tweet.id}'


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f'@{self.user.username} bookmarked tweet {self.tweet.id}'


class FlagReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('action_taken', 'Action Taken'),
        ('dismissed', 'Dismissed (False Positive)'),
    ]

    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='flag_reports', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='flag_reports', null=True, blank=True)
    detected_label = models.CharField(max_length=20)
    confidence_score = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_reports'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'FlagReport #{self.id} - {self.detected_label} ({self.status})'

    def get_label_display_name(self):
        return self.detected_label.replace('_', ' ').title()