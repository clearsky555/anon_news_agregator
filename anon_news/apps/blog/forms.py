from django import forms
from apps.blog.models import Post, Comment


class PostCreationForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            'title',
            'image',
            'description',
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),

        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'image', 'reply_for']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'id':"comment_input"}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'reply_for': forms.HiddenInput(),
        }

    enctype = 'multipart/form-data'
