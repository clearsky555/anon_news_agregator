from django import forms

from apps.community.models import Community


class CommunityCreationForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['title', 'slug', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }