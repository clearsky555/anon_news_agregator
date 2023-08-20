from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Post


@receiver(post_save, sender=Post)
def delete_inactive_posts(sender, instance, **kwargs):
    threshold = timezone.now() - timedelta(hours=48)


    inactive_posts = Post.objects.filter(commented_at__lte=threshold)

    print('-------------')
    print(inactive_posts)
    print('-------------')

    inactive_posts.delete()