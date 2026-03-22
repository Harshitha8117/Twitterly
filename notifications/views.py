from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(recipient=request.user).select_related('sender', 'tweet')
    # Mark all as read
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/notifications.html', {'notifications': notifs})


@login_required
def mark_read(request, notif_id):
    Notification.objects.filter(pk=notif_id, recipient=request.user).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
def unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})
