from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from apps.chat.models import Chat


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
    return render(request, "chat/room.html", {"room_name": room_name})


# СЮДА НУЖНО ДОБАВИТЬ БЕЗОПАСНОСТЬ!!!
def delete_chat(request, chat_name):
    chat = get_object_or_404(Chat, name=chat_name)
    chat.delete()
    queryset = request.user.chats.all()
    context = {
        'chats': queryset,
    }
    return render(request, "chat/index.html", context)

