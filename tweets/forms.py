from django import forms
from .models import Tweet, Comment


class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control tweet-input',
                'placeholder': "What's happening?",
                'rows': 3,
                'maxlength': 280,
                'id': 'tweet-content'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'tweet-image'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Post your reply',
                'rows': 2,
                'maxlength': 280,
            }),
        }


class QuoteTweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add a comment...',
                'rows': 2,
                'maxlength': 280,
            }),
        }
