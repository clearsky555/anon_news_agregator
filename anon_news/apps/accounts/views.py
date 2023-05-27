from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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


class Profile(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['user'] = User.objects.get(id=pk)
        return context


class UserRegisterView(CreateView):
    model = User
    template_name = 'register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('register_done')


class RegisterDoneView(TemplateView):
    template_name = 'register_done.html'


@login_required
def save_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if image_file:
            request.user.image = image_file
            request.user.save()
    return redirect('all')