from .models import Hashtag
from django.db.models import Count


def trending_hashtags(request):
    trending = Hashtag.objects.annotate(
        tweet_count=Count('tweet')
    ).order_by('-tweet_count')[:5]
    return {'trending_hashtags': trending}
