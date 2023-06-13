from django.db import models

from apps.accounts.models import User


# Create your models here.
class Community(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communities')
    title = models.CharField(verbose_name='название сообщества', max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(verbose_name='описание сообщества', null=True)
    subscribers = models.ManyToManyField(User, related_name='sub_communities')
    is_private = models.BooleanField(default=False)
    application = models.ManyToManyField(User, related_name='membership_applications')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return f'{self.title}'