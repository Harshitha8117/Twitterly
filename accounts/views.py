from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import User
from .forms import RegisterForm, LoginForm, ProfileEditForm
from tweets.models import Tweet


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Twitterly, @{user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_blocked:
                messages.error(request, 'Your account has been blocked due to policy violations. Contact support.')
                return render(request, 'accounts/login.html', {'form': form})
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(author=profile_user, is_deleted=False).order_by('-created_at')
    is_following = request.user.is_following(profile_user)
    context = {
        'profile_user': profile_user,
        'tweets': tweets,
        'is_following': is_following,
        'followers_count': profile_user.get_followers_count(),
        'following_count': profile_user.get_following_count(),
        'tweets_count': tweets.count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def follow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    if request.user.is_following(target_user):
        request.user.following.remove(target_user)
        is_following = False
    else:
        request.user.following.add(target_user)
        is_following = True
        # Create notification
        from notifications.models import Notification
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notif_type='follow',
            message=f'@{request.user.username} started following you.'
        )

    return JsonResponse({
        'is_following': is_following,
        'followers_count': target_user.get_followers_count()
    })


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(pk=request.user.pk)[:10]
    return render(request, 'accounts/search.html', {'users': users, 'query': query})


@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = profile_user.followers.all()
    return render(request, 'accounts/follow_list.html', {
        'profile_user': profile_user, 'users': followers, 'list_type': 'Followers'
    })


@login_required
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = profile_user.following.all()
    return render(request, 'accounts/follow_list.html', {
        'profile_user': profile_user, 'users': following, 'list_type': 'Following'
    })
