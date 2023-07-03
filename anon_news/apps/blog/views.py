from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from apps.accounts.models import User, BannedIP
from apps.blog.models import Post, Category, Comment, Notification
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from apps.blog.forms import PostCreationForm, CommentForm
from django.shortcuts import redirect
from django.utils import timezone

from apps.community.models import Community


class PostListView(ListView):
    template_name = 'index.html'
    model = Post
    # queryset = Post.objects.all()
    queryset = Post.objects.order_by('-created_at')  # Упорядочить посты по убыванию времени создания
    context_object_name = 'posts'
    paginate_by = 15


class PopularPostListView(ListView):
    template_name = 'index.html'
    model = Post
    queryset = Post.objects.annotate(total_likes=Count('likes') - Count('dislikes')).order_by('-total_likes')
    context_object_name = 'posts'
    paginate_by = 15


class DiscussPostListView(ListView):
    template_name = 'index.html'
    model = Post
    queryset = Post.objects.annotate(comment_count=Count('post_comments')).order_by('-comment_count')
    context_object_name = 'posts'
    paginate_by = 15


class PostDetailView(DetailView):
    template_name = 'post_detail.html'
    model = Post
    queryset = Post.objects.all()
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comment_form'] = CommentForm()
        context['community'] = post.community
        return context


class PostCreateView(CreateView):
    template_name = 'post_create.html'
    model = Post
    success_url = reverse_lazy('all')
    form_class = PostCreationForm

    def get_ip_address(self, request):
        user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip_address:
            ip = user_ip_address.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def form_valid(self, form):
        post = form.save(commit=False)
        if 'anonymous' in self.request.POST and self.request.POST['anonymous'] == 'on' or self.request.user.is_authenticated == False:
            post.author = None
        else:
            post.author = self.request.user

        community_slug = self.kwargs.get('community_slug')
        if community_slug:
            community = get_object_or_404(Community, slug=community_slug)
            post.community = community
        else:
            post.community = None

        try:
            post.ip_address = self.get_ip_address(self.request)  # Сохраняем IP-адрес
            post.save()
        except ValueError:
            raise Http404("Invalid community_slug")

        return super().form_valid(form)


def save_comment_form(request, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            post = get_object_or_404(Post, id=post_id)
            comment = form.save(commit=False)

            if 'anonymous' in request.POST and request.POST['anonymous'] == 'on' or request.user.is_authenticated==False:
                comment.author = None
            else:
                comment.author = request.user

            comment.post = post
            comment.is_parent = True

            # Получаем IP-адрес из HTTP-запроса
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip = ip_address.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            comment.ip_address = ip

            comment.save()
            # Notification.objects.create(
            #     user=post.author,  # уведомление для автора поста
            #     post=post,
            #     comment=comment,
            #
            #     is_read=False,
            #     created_at=timezone.now()
            # )
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


def save_comment_reply_form(request, post_id, comment_id):
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
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

            # Получаем IP-адрес из HTTP-запроса
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip = ip_address.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            comment.ip_address = ip
            
            comment.save()

            # Создаем объект уведомления при реплае к комментарию
            Notification.objects.create(
                user=parent_comment.author,  # Автору комментария, на который был оставлен реплай
                post=post,
                comment=comment,
                reply_to_comment=parent_comment,
                is_read=False,
                created_at=timezone.now(),
                message=f'{comment.author} ответил на ваш комментарий {comment}'
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
                created_at=timezone.now(),
                message=f'вашему посту {post} поставил лайк пользователь {user}'
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
                created_at=timezone.now(),
                message=f'вашему посту {post} поставил дизлайк пользователь {user}'

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
                created_at=timezone.now(),
                message=f'вашему комментарию {comment} поставил лайк пользователь {user}'

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
                created_at=timezone.now(),
                message=f'вашему комментарию {comment} поставил дизлайк пользователь {user}'

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


@login_required
def delete_post(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    community = post.community
    print('-----------')
    print(community)
    print('-----------')
    if user.is_staff or user == community.creator:
        post.delete()
    else:
        return redirect('forbidden')
    return redirect(reverse_lazy('all'))


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    community = post.community
    if user.is_staff or user == community.creator:
        comment.author = None
        comment.text = 'комментарий удален'
        comment.save()
    else:
        return redirect('forbidden')
    return redirect(reverse_lazy('post_detail', kwargs={'pk': post_id}))


@login_required
def post_permaban(request, pk):
    user = request.user
    post = get_object_or_404(Post, id=pk)
    ip_address = post.ip_address
    print('------IP------')
    print(ip_address)
    print(f'------{post}------')
    if user.is_staff:
        ip = BannedIP.objects.create(ip_address=ip_address)
        ip.save()
    else:
        return redirect('forbidden')

    return redirect('all')


@login_required
def comment_permaban(request, pk):
    user = request.user
    comment = get_object_or_404(Comment, id=pk)
    ip_address = comment.ip_address
    print('------IP------')
    print(ip_address)
    print(f'------{comment}------')
    if user.is_staff:
        ip = BannedIP.objects.create(ip_address=ip_address)
        ip.save()
    else:
        return redirect('forbidden')

    return redirect('all')