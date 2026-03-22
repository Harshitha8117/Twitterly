from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from .models import Tweet, Comment, Like, Bookmark, FlagReport, Hashtag
from .forms import TweetForm, CommentForm, QuoteTweetForm
from ml_engine.predictor import analyze_text
from notifications.models import Notification


def run_ml_check(tweet):
 
    result = analyze_text(tweet.content)
    tweet.flag_reason = result['label']
    tweet.flag_confidence = result['confidence']
    if result['is_harmful']:
        tweet.is_flagged = True
        FlagReport.objects.create(
            tweet=tweet,
            detected_label=result['label'],
            confidence_score=result['confidence'],
            status='pending'
        )
    tweet.save()
    return result


def run_ml_check_comment(comment):

    result = analyze_text(comment.content)
    comment.flag_reason = result['label']
    comment.flag_confidence = result['confidence']
    if result['is_harmful']:
        comment.is_flagged = True
        FlagReport.objects.create(
            comment=comment,
            detected_label=result['label'],
            confidence_score=result['confidence'],
            status='pending'
        )
    comment.save()
    return result


@login_required
def home(request):
    user = request.user
    # Feed: tweets from followed users + own tweets
    following_ids = list(user.following.values_list('pk', flat=True)) + [user.pk]
    tweets = Tweet.objects.filter(
        author__id__in=following_ids, is_deleted=False
    ).select_related('author', 'original_tweet__author').prefetch_related('likes', 'hashtags')

    # Who to follow suggestions
    suggestions = suggest_users(user)

    form = TweetForm()
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.author = user
            tweet.save()
            tweet.save_hashtags()
            run_ml_check(tweet)
            if not tweet.is_flagged:
                messages.success(request, 'Tweet posted!')
            # Do NOT show flag warning to user - only admin sees flagged content
            return redirect('home')

    context = {
        'tweets': tweets,
        'form': form,
        'suggestions': suggestions,
    }
    return render(request, 'tweets/home.html', context)


def suggest_users(user):
    from accounts.models import User
    following_ids = list(user.following.values_list('pk', flat=True)) + [user.pk]
    return User.objects.exclude(pk__in=following_ids).order_by('?')[:3]


@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, is_deleted=False)
    comments = tweet.comments.filter(is_deleted=False, parent=None)
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.tweet = tweet
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(pk=parent_id)
                except Comment.DoesNotExist:
                    pass
            comment.save()
            run_ml_check_comment(comment)

            # Notify tweet author
            if tweet.author != request.user:
                Notification.objects.create(
                    recipient=tweet.author,
                    sender=request.user,
                    notif_type='reply',
                    tweet=tweet,
                    message=f'@{request.user.username} replied to your tweet.'
                )
            return redirect('tweet_detail', tweet_id=tweet_id)

    return render(request, 'tweets/tweet_detail.html', {
        'tweet': tweet,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def like_toggle(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, is_deleted=False)
    like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True
        if tweet.author != request.user:
            Notification.objects.create(
                recipient=tweet.author,
                sender=request.user,
                notif_type='like',
                tweet=tweet,
                message=f'@{request.user.username} liked your tweet.'
            )
    return JsonResponse({'is_liked': is_liked, 'likes_count': tweet.get_likes_count()})


@login_required
def retweet_toggle(request, tweet_id):
    original = get_object_or_404(Tweet, pk=tweet_id, is_deleted=False)
    existing = Tweet.objects.filter(
        original_tweet=original, author=request.user, is_retweet=True, is_deleted=False
    ).first()

    if existing:
        existing.is_deleted = True
        existing.save()
        is_retweeted = False
    else:
        rt = Tweet.objects.create(
            author=request.user,
            content=original.content,
            is_retweet=True,
            original_tweet=original
        )
        is_retweeted = True
        if original.author != request.user:
            Notification.objects.create(
                recipient=original.author,
                sender=request.user,
                notif_type='retweet',
                tweet=original,
                message=f'@{request.user.username} retweeted your tweet.'
            )
    return JsonResponse({'is_retweeted': is_retweeted, 'retweets_count': original.get_retweets_count()})


@login_required
def quote_tweet(request, tweet_id):
    original = get_object_or_404(Tweet, pk=tweet_id, is_deleted=False)
    if request.method == 'POST':
        form = QuoteTweetForm(request.POST)
        if form.is_valid():
            qt = form.save(commit=False)
            qt.author = request.user
            qt.is_retweet = True
            qt.original_tweet = original
            qt.quote_content = form.cleaned_data['content']
            qt.content = form.cleaned_data['content']
            qt.save()
            qt.save_hashtags()
            run_ml_check(qt)
            messages.success(request, 'Quote tweet posted!')
        return redirect('home')
    return redirect('tweet_detail', tweet_id=tweet_id)


@login_required
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, author=request.user)
    tweet.is_deleted = True
    tweet.save()
    messages.success(request, 'Tweet deleted.')
    return redirect('home')


@login_required
def bookmark_toggle(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, is_deleted=False)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, tweet=tweet)
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True
    return JsonResponse({'is_bookmarked': is_bookmarked})


@login_required
def bookmarks(request):
    bookmarked = Bookmark.objects.filter(user=request.user).select_related('tweet__author').order_by('-created_at')
    tweets = [b.tweet for b in bookmarked if not b.tweet.is_deleted]
    return render(request, 'tweets/bookmarks.html', {'tweets': tweets})


@login_required
def explore(request):
    # Trending hashtags
    trending = Hashtag.objects.annotate(
        tweet_count=Count('tweet')
    ).order_by('-tweet_count')[:10]

    query = request.GET.get('q', '')
    tweets = []
    if query:
        tweets = Tweet.objects.filter(
            Q(content__icontains=query), is_deleted=False
        ).select_related('author').order_by('-created_at')

    return render(request, 'tweets/explore.html', {
        'trending': trending,
        'tweets': tweets,
        'query': query,
    })


@login_required
def hashtag_tweets(request, tag):
    hashtag = get_object_or_404(Hashtag, name=tag.lower())
    tweets = Tweet.objects.filter(hashtags=hashtag, is_deleted=False).select_related('author').order_by('-created_at')
    return render(request, 'tweets/hashtag.html', {'hashtag': hashtag, 'tweets': tweets})

@login_required
def tweet_status(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, is_deleted=False)
    return JsonResponse({
        'is_liked': tweet.likes.filter(user=request.user).exists(),
        'is_retweeted': Tweet.objects.filter(original_tweet=tweet, author=request.user, is_retweet=True, is_deleted=False).exists(),
        'is_bookmarked': tweet.bookmarks.filter(user=request.user).exists(),
    })

