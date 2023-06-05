from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from apps.accounts.models import User
from apps.blog.models import Post, Category, Comment, Notification
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from apps.blog.forms import PostCreationForm, CommentForm
from django.shortcuts import redirect
from django.utils import timezone


class PostListView(ListView):
    template_name = 'index.html'
    model = Post
    # queryset = Post.objects.all()
    queryset = Post.objects.order_by('-created_at')  # Упорядочить посты по убыванию времени создания
    context_object_name = 'posts'


class PopularPostListView(ListView):
    template_name = 'index.html'
    model = Post
    queryset = Post.objects.annotate(total_likes=Count('likes') - Count('dislikes')).order_by('-total_likes')
    context_object_name = 'posts'


class DiscussPostListView(ListView):
    template_name = 'index.html'
    model = Post
    queryset = Post.objects.annotate(comment_count=Count('post_comments')).order_by('-comment_count')
    context_object_name = 'posts'


class PostDetailView(DetailView):
    template_name = 'post_detail.html'
    model = Post
    queryset = Post.objects.all()
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


class PostCreateView(CreateView):
    template_name = 'post_create.html'
    model = Post
    success_url = reverse_lazy('all')
    form_class = PostCreationForm

    def form_valid(self, form):
        post = form.save(commit=False)
        if 'anonymous' in self.request.POST and self.request.POST['anonymous'] == 'on' or self.request.user.is_authenticated == False:
            post.author = None
        else:
            post.author = self.request.user
        post.save()
        return super().form_valid(form)


def save_comment_form(request, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, id=post_id)
            comment = form.save(commit=False)

            if 'anonymous' in request.POST and request.POST['anonymous'] == 'on' or request.user.is_authenticated==False:
                comment.author = None
            else:
                comment.author = request.user

            comment.post = post
            comment.is_parent = True
            comment.save()
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


def save_comment_reply_form(request, post_id, comment_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, id=post_id)
            comment = form.save(commit=False)
            parent_comment = get_object_or_404(Comment, id=comment_id)
            comment.reply_for = parent_comment

            if 'anonymous' in request.POST and request.POST['anonymous'] == 'on' or request.user.is_authenticated==False:
                comment.author = None
            else:
                comment.author = request.user

            comment.post = post
            comment.save()

            # Создаем объект уведомления при реплае к комментарию
            Notification.objects.create(
                user=parent_comment.author,  # Автору комментария, на который был оставлен реплай
                post=post,
                comment=comment,
                reply_to_comment=parent_comment,
                is_read=False,
                created_at=timezone.now()
            )
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.dislikes.all():
        post.dislikes.remove(user)

    if user not in post.likes.all():
        post.likes.add(user)
        # Проверяем наличие существующего уведомления
        existing_notification = Notification.objects.filter(user=post.author, post=post, post_liker=user).first()
        if not existing_notification:

            # Создаем объект Notification при лайке
            Notification.objects.create(
                user=post.author,  # Автору поста
                post=post,
                post_liker=user,  # Пользователь, который поставил лайк посту
                liked_post=post,
                is_read=False,
                created_at=timezone.now()
            )
    else:
        post.likes.remove(user)
    post.save()
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)

    if user not in post.dislikes.all():
        post.dislikes.add(user)
        existing_notification = Notification.objects.filter(user=post.author, post=post, post_disliker=user).first()
        if not existing_notification:
            # Создаем объект Notification при лайке
            Notification.objects.create(
                user=post.author,  # Автору поста
                post=post,
                post_disliker=user,  # Пользователь, который поставил лайк посту
                liked_post=post,
                is_read=False,
                created_at=timezone.now()
            )
    else:
        post.dislikes.remove(user)
    post.save()
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    post_id = comment.post_id

    if user in comment.dislikes.all():
        comment.dislikes.remove(user)

    if user not in comment.likes.all():
        comment.likes.add(user)
        existing_notification = Notification.objects.filter(user=comment.post.author, post=comment.post, comment=comment, comment_liker=user).first()

        if not existing_notification:
            Notification.objects.create(
                user=comment.author,  # тот, кому придет уведомление, автор комментария
                post=comment.post,
                comment=comment,
                comment_liker=user,  # Пользователь, который поставил лайк комменту
                liked_post=comment.post,
                is_read=False,
                created_at=timezone.now()
            )
    else:
        comment.likes.remove(user)
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    post_id = comment.post_id

    if user in comment.likes.all():
        comment.likes.remove(user)

    if user not in comment.dislikes.all():
        comment.dislikes.add(user)
        existing_notification = Notification.objects.filter(user=comment.post.author, post=comment.post, comment=comment, comment_disliker=user).first()

        if not existing_notification:

            Notification.objects.create(
                user=comment.author,  # тот, кому придет уведомление, автор комментария
                post=comment.post,
                comment=comment,
                comment_disliker=user,  # Пользователь, который поставил лайк
                liked_post=comment.post,
                is_read=False,
                created_at=timezone.now()
            )
    else:
        comment.dislikes.remove(user)
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


class NotificationView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        user = self.request.user
        qs = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')
        # qs.update(is_read=True)
        return qs

    def get_text(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        context['unread_count'] = unread_count
        return context


def mark_notifications_as_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications')