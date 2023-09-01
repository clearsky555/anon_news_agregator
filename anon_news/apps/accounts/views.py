import os
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView, CreateView, TemplateView, ListView
from apps.accounts.forms import LoginForm, UserRegisterForm
from django.http import HttpResponse
from apps.accounts.models import User, BannedIP
from django.urls import reverse_lazy

from apps.blog.models import Notification
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
        context['profile_user'] = self.request.user

        return context

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        some_user = User.objects.get(id=pk)
        post_list = some_user.posts.all()
        comment_list = some_user.comments.all()
        paginator = Paginator(post_list, 5)  # Show 5 posts per page.
        comment_paginator = Paginator(comment_list, 5)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        comment_page_obj = comment_paginator.get_page(page_number)
        context = {
            "page_obj": page_obj,
            'comment_page_obj': comment_page_obj,
            "some_user": some_user,
            "profile_user": self.request.user
        }
        return render(request, "profile.html", context)


@login_required
def send_message(request, user_id):
    some_user = User.objects.get(id=user_id)
    user = request.user
    user_chats = user.chats.filter(participants__in=[user, some_user]).filter(participants=some_user)
    existing_chat = None
    for c in user_chats:
        if c.participants.count() == 2:
            existing_chat = c
            break
    # chats = some_user.chats.filter(participants__in=[user, some_user]).filter(participants=user).order_by('-participants')


    # existing_chat = Chat.objects.filter(participants=some_user).filter(participants=request.user).annotate(
    #     user_count=Count('participants')).order_by('-user_count')
    # print(existing_chat)
    # print('existing_chat-------------------')

    if existing_chat:
        return redirect('room', existing_chat.name)
    else:
        # Создаем новый диалог
        room_name = str(uuid.uuid4())
        Chat.objects.create(name=room_name)
        chat_instance = Chat.objects.get(name=room_name)
        chat_instance.participants.add(some_user, request.user)
        chat_instance.save()
        return redirect('room', room_name)


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


class AddUser(LoginRequiredMixin, ListView):
    template_name = 'adduser.html'
    model = Chat
    context_object_name = 'chats'

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(participants=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['pk']
        user = get_object_or_404(User, id=user_id)
        context['user_being_added'] = user
        return context


@login_required
def adduser2(request, chat_name, user_id):
    chat = Chat.objects.get(name=chat_name)
    user = User.objects.get(id=user_id)
    if request.user not in chat.participants.all():
        return redirect('forbidden')
    chat.participants.add(user)
    chat.save()
    Notification.objects.create(
                user=user,
                message=f'{request.user} пригласил вас в общий чат',
            )
    return redirect('all')


from rest_framework.generics import CreateAPIView
from rest_framework.permissions import  AllowAny
from rest_framework.response import Response
from apps.api.serializers import CreateUserSerializer


class CreateUserAPIView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        message = "User registered successfully"
        return Response(data={"message":message, "data":response.data})