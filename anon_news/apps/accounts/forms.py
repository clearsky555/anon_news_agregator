from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'юзернейм'}),
        label='юзернейм'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'пароль'}),
        label='Пароль'
    )


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'юзернейм'}),
        label='юзернейм'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'придумайте пароль'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'подтвердите пароль'})
    )

    class Meta:
        model = User
        fields = [
            'username',
        ]