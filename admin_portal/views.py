from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from tweets.models import Tweet, FlagReport, Comment
from accounts.models import User
from notifications.models import Notification
import json


def admin_required(view_func):
    decorated = staff_member_required(view_func, login_url='/admin-portal/login/')
    return decorated


@admin_required
def dashboard(request):
    total_users = User.objects.count()
    total_tweets = Tweet.objects.filter(is_deleted=False).count()
    total_flagged = Tweet.objects.filter(is_flagged=True, is_deleted=False).count()
    pending_reports = FlagReport.objects.filter(status='pending').count()

    # Today's stats
    today = timezone.now().date()
    flagged_today = FlagReport.objects.filter(created_at__date=today).count()
    new_users_today = User.objects.filter(date_joined__date=today).count()

    # Label distribution
    hate_count = FlagReport.objects.filter(detected_label='hate_speech').count()
    cyber_count = FlagReport.objects.filter(detected_label='cyberbullying').count()
    normal_count = total_tweets - total_flagged

    # Recent flags
    recent_flags = FlagReport.objects.filter(status='pending').select_related(
        'tweet__author', 'comment__author'
    ).order_by('-created_at')[:10]

    # Blocked / warned users
    blocked_users = User.objects.filter(is_blocked=True).count()
    warned_users = User.objects.filter(is_warned=True).count()

    # Load ML metrics if model is trained
    ml_metrics = None
    try:
        import joblib
        from django.conf import settings
        metrics_path = str(settings.ML_MODEL_PATH) + "/metrics.pkl"
        import os
        if os.path.exists(metrics_path):
            ml_metrics = joblib.load(metrics_path)
    except Exception:
        pass

    context = {
        'total_users': total_users,
        'total_tweets': total_tweets,
        'total_flagged': total_flagged,
        'pending_reports': pending_reports,
        'flagged_today': flagged_today,
        'new_users_today': new_users_today,
        'hate_count': hate_count,
        'cyber_count': cyber_count,
        'normal_count': normal_count,
        'recent_flags': recent_flags,
        'blocked_users': blocked_users,
        'warned_users': warned_users,
        'ml_metrics': ml_metrics,
    }
    return render(request, 'admin_portal/dashboard.html', context)


@admin_required
def flagged_content(request):
    status_filter = request.GET.get('status', 'pending')
    label_filter = request.GET.get('label', '')

    reports = FlagReport.objects.select_related(
        'tweet__author', 'comment__author', 'reviewed_by'
    ).order_by('-created_at')

    if status_filter:
        reports = reports.filter(status=status_filter)
    if label_filter:
        reports = reports.filter(detected_label=label_filter)

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'label_filter': label_filter,
    }
    return render(request, 'admin_portal/flagged.html', context)


@admin_required
def report_detail(request, report_id):
    report = get_object_or_404(FlagReport, pk=report_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        note = request.POST.get('admin_note', '')

        report.admin_note = note
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()

        if action == 'dismiss':
            report.status = 'dismissed'
            if report.tweet:
                report.tweet.is_flagged = False
                report.tweet.save()
            report.save()

        elif action == 'warn_user':
            report.status = 'action_taken'
            report.save()
            target_user = report.tweet.author if report.tweet else report.comment.author
            target_user.is_warned = True
            target_user.warning_count += 1
            target_user.save()
            Notification.objects.create(
                recipient=target_user,
                notif_type='warning',
                message=f'⚠️ Your account has received a warning for violating our community guidelines. '
                        f'Reason: {report.detected_label.replace("_", " ").title()}. '
                        f'Further violations may result in account suspension.'
            )

        elif action == 'delete_tweet':
            report.status = 'action_taken'
            report.save()
            if report.tweet:
                report.tweet.is_deleted = True
                report.tweet.save()
                Notification.objects.create(
                    recipient=report.tweet.author,
                    notif_type='system',
                    message=f'Your tweet was removed for violating our community guidelines ({report.detected_label.replace("_", " ").title()}).'
                )
            elif report.comment:
                report.comment.is_deleted = True
                report.comment.save()

        elif action == 'block_user':
            report.status = 'action_taken'
            report.save()
            target_user = report.tweet.author if report.tweet else report.comment.author
            target_user.is_blocked = True
            target_user.save()
            Notification.objects.create(
                recipient=target_user,
                notif_type='system',
                message='Your account has been suspended due to repeated violations of our community guidelines.'
            )

        return redirect('admin_flagged')

    # Resolve target user safely
    target_user = None
    if report.tweet and report.tweet.author:
        target_user = report.tweet.author
    elif report.comment and report.comment.author:
        target_user = report.comment.author

    return render(request, 'admin_portal/report_detail.html', {
        'report': report,
        'target_user': target_user,
    })


@admin_required
def user_management(request):
    search = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')

    users = User.objects.all().annotate(
        tweet_count=Count('tweets'),
        flag_count=Count('tweets__flag_reports'),
    ).order_by('-date_joined')

    if search:
        users = users.filter(
            Q(username__icontains=search) | Q(email__icontains=search) |
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    if filter_type == 'blocked':
        users = users.filter(is_blocked=True)
    elif filter_type == 'warned':
        users = users.filter(is_warned=True)
    elif filter_type == 'staff':
        users = users.filter(is_staff=True)

    return render(request, 'admin_portal/users.html', {
        'users': users,
        'search': search,
        'filter_type': filter_type,
    })


@admin_required
def toggle_block_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user.is_staff:
        return JsonResponse({'error': 'Cannot block admin users'}, status=400)
    target_user.is_blocked = not target_user.is_blocked
    target_user.save()
    if target_user.is_blocked:
        Notification.objects.create(
            recipient=target_user,
            notif_type='system',
            message='Your account has been suspended by an administrator.'
        )
    return JsonResponse({'is_blocked': target_user.is_blocked})


@admin_required
def user_detail(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    tweets = Tweet.objects.filter(author=target_user, is_deleted=False).order_by('-created_at')[:20]
    flagged_tweets = Tweet.objects.filter(author=target_user, is_flagged=True, is_deleted=False)
    reports = FlagReport.objects.filter(tweet__author=target_user).order_by('-created_at')[:10]

    return render(request, 'admin_portal/user_detail.html', {
        'target_user': target_user,
        'tweets': tweets,
        'flagged_tweets': flagged_tweets,
        'reports': reports,
    })


def admin_login_view(request):
    """Dedicated admin login page."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    error = None
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                error = 'This account does not have admin privileges.'
        else:
            error = 'Invalid username or password.'

    return render(request, 'admin_portal/login.html', {'error': error})
