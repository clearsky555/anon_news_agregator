from django.db import models
from apps.accounts.models import User


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
    image = models.ImageField(verbose_name='Картинка', upload_to='posts/images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    likes = models.ManyToManyField(User, related_name='liked_posts')
    dislikes = models.ManyToManyField(User, related_name='disliked_posts')


    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    text = models.TextField('Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    # reply_for = models.ForeignKey('self', on_delete=models.CASCADE)
    # image = models.ImageField('Картинка', null=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text}'
