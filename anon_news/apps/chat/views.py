from django.shortcuts import render
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
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})