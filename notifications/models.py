from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    NOTIF_TYPES = [
        ('like', 'Like'),
        ('follow', 'Follow'),
        ('reply', 'Reply'),
        ('retweet', 'Retweet'),
        ('warning', 'Warning'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_notifications', null=True, blank=True
    )
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    tweet = models.ForeignKey(
        'tweets.Tweet', on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for @{self.recipient.username}: {self.message[:50]}'

    def get_icon(self):
        icons = {
            'like': '❤️',
            'follow': '👤',
            'reply': '💬',
            'retweet': '🔁',
            'warning': '⚠️',
            'system': '🔔',
        }
        return icons.get(self.notif_type, '🔔')
