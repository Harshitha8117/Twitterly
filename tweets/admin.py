from django.contrib import admin
from .models import Tweet, Comment, Like, Bookmark, FlagReport, Hashtag
admin.site.register(Tweet)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Bookmark)
admin.site.register(FlagReport)
admin.site.register(Hashtag)
