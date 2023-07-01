import os
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView, CreateView, TemplateView
from apps.accounts.forms import LoginForm, UserRegisterForm
from django.http import HttpResponse
from apps.accounts.models import User, BannedIP
from django.urls import reverse_lazy

from apps.chat.models import Chat

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
        some_user = User.objects.get(id=pk)

        context['some_user'] = some_user
        context['profile_user'] = self.request.user  # Добавляем переменную profile_user в контекст
        print('--------------')
        print(self.request.user)
        print('--------------')

        if not isinstance(self.request.user, AnonymousUser):
            existing_chat = Chat.objects.filter(participants=some_user).filter(participants=self.request.user).first()

            if existing_chat:
                context['room_name'] = existing_chat.name
            else:
                # Создаем новый диалог
                room_name = str(uuid.uuid4())
                Chat.objects.create(name=room_name)
                chat_instance = Chat.objects.get(name=room_name)
                chat_instance.participants.add(some_user, self.request.user)
                chat_instance.save()
                context['room_name'] = room_name
        else:
            context['room_name'] = 'anon'

        return context


class UserRegisterView(CreateView):
    model = User
    template_name = 'register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('register_done')

    def form_valid(self, form):
        user_ip_address = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip_address:
            ip = user_ip_address.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        form.instance.ip_address = ip
        return super().form_valid(form)


class RegisterDoneView(TemplateView):
    template_name = 'register_done.html'


@login_required
def save_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if request.user.image and os.path.basename(request.user.image.name) != 'default55555.png':
            request.user.image.delete()

        if image_file:
            request.user.image = image_file
            request.user.save()
    return redirect('all')


@login_required
def permaban(request, pk):
    user = request.user
    ban_user = get_object_or_404(User, pk=pk)
    ip_address = ban_user.ip_address
    print('------IP------')
    print(ip_address)
    print(f'------{ban_user}------')
    if user.is_staff:
        ip = BannedIP.objects.create(ip_address=ip_address)
        ip.save()
    else:
        return redirect('forbidden')

    return redirect('all')