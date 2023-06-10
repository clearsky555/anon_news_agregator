from django.utils import timezone

from django.db import models
from apps.accounts.models import User
import re
from django.utils.safestring import mark_safe
from django.urls import reverse

from apps.community.models import Community


class Category(models.Model):
    name = models.CharField(verbose_name='Название категории', max_length=100)
    slug = models.SlugField(max_length=150)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    title = models.CharField(verbose_name='Название поста', max_length=255)
    description = models.TextField(verbose_name='Тело поста')
    image = models.ImageField(verbose_name='Картинка', upload_to='posts/images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    likes = models.ManyToManyField(User, related_name='liked_posts')
    dislikes = models.ManyToManyField(User, related_name='disliked_posts')
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, related_name='community_posts')


    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.title}'


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    text = models.TextField('Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    reply_for = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    image = models.ImageField('Картинка', upload_to='comments/images/', blank=True, null=True)
    is_parent = models.BooleanField('self', default=False)

    likes = models.ManyToManyField(User, related_name='liked_comments')
    dislikes = models.ManyToManyField(User, related_name='disliked_comments')

    def save(self, *args, **kwargs):
        created = not self.pk  # Check if a new comment is being created or an existing one is being updated
        super().save(*args, **kwargs)

        if created:
            existing_notification = Notification.objects.filter(user=self.post.author, post=self.post, comment=self).first()
            if not existing_notification:
                # Create a notification only for the author of the post
                Notification.objects.create(
                    user=self.post.author,
                    post=self.post,
                    comment=self,
                    is_read=False,
                    created_at=timezone.now(),
                    message=f'в вашем посте {self.post} появился новый комментарий от {self.author}',
                )


    def formatted_text(self):
        # Парсинг текста комментария и замена ссылок на изображения на соответствующий HTML-код
        text = self.text
        # Регулярное выражение для поиска ссылок на изображения
        image_regex = r'(https?://\S+\.(?:gif|jpe?g|png|webp))'
        # Замена ссылок на изображения на HTML-тег <img>
        formatted_text = re.sub(image_regex, r'<img src="\1" style="max-width: 500px;">', text)
        return mark_safe(formatted_text)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    reply_to_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_replies')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    post_liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_notifications', null=True)
    post_disliker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disliked_notifications', null=True)
    comment_liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_liked_notifications', null=True)
    comment_disliker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_disliked_notifications', null=True)
    liked_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked_notifications', null=True)
    message = models.TextField(null=True)
    class Meta:
        ordering = ['-created_at']
