from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView, CreateView, TemplateView
from apps.accounts.forms import LoginForm, UserRegisterForm
from django.http import HttpResponse
from apps.accounts.models import User
from django.urls import reverse_lazy


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        data = form.cleaned_data
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return redirect('all')
            else:
                HttpResponse('Ваш аккаунт не активен')
        HttpResponse('Такого пользователя не существует')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('all')


class UserRegisterView(CreateView):
    model = User
    template_name = 'register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('register_done')


class RegisterDoneView(TemplateView):
    template_name = 'register_done.html'