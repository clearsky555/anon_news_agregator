from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from apps.chat.models import Chat, Message


# Create your views here.
# class DialoguesListView(ListView):
#     template_name = 'dialogues.html'
#     model = Chat
#     # queryset = Chat.objects.all()
#     context_object_name = 'dialogues'
#
#     def get_queryset(self):
#         user = self.request.user
#         chats = user.chats.all()
#         return chats


def index(request):
    queryset = request.user.chats.all()
    context = {
        'chats': queryset,
    }

    return render(request, "chat/index.html", context)


def room(request, room_name):
    # Получить объект чата по имени комнаты
    chat = Chat.objects.get(name=room_name)

    # Получите все сообщения для данного чата
    messages = Message.objects.filter(chat=chat)
    if request.user not in chat.participants.all():
        return redirect('forbidden')

    context = {
        "room_name": room_name,
        "messages": messages,
    }
    return render(request, "chat/room.html", context)


@login_required
def delete_chat(request, chat_name):
    chat = get_object_or_404(Chat, name=chat_name)
    if request.user not in chat.participants.all():
        return redirect('forbidden')
    chat.delete()
    queryset = request.user.chats.all()
    context = {
        'chats': queryset,
    }
    return render(request, "chat/index.html", context)

