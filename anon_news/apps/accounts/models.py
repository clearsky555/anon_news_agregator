import os

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Sum
from django.http import HttpResponseForbidden


def default_avatar_path():
    return os.path.join('images', 'default55555.png')


class UserManager(BaseUserManager):
    pass


class User(AbstractUser):
    username = models.CharField(unique=True, max_length=150)
    image = models.ImageField('аватарка', upload_to='user/images/', default='user/default55555.png')
    is_staff = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'

    def total_likes(self):
        post_likes = self.posts.filter(likes__in=User.objects.exclude(id=self.id)).count()
        comment_likes = self.comments.filter(likes__in=User.objects.exclude(id=self.id)).count()

        post_likes = post_likes if post_likes is not None else 0
        comment_likes = comment_likes if comment_likes is not None else 0

        return post_likes + comment_likes

    def total_dislikes(self):
        post_dislikes = self.posts.filter(dislikes__in=User.objects.exclude(id=self.id)).count()
        comment_dislikes = self.comments.filter(dislikes__in=User.objects.exclude(id=self.id)).count()

        post_dislikes = post_dislikes if post_dislikes is not None else 0
        comment_dislikes = comment_dislikes if comment_dislikes is not None else 0

        return (post_dislikes + comment_dislikes)*(-1)


class BannedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    banned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ip_address}'


class BannedIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        if BannedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Доступ запрещен")

        response = self.get_response(request)
        return response