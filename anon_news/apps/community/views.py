from django.contrib import messages as mssgs
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, RedirectView

from apps.accounts.models import User
from apps.community.forms import CommunityCreationForm
from apps.community.models import Community


# Create your views here.
class CommunityCreateView(LoginRequiredMixin, CreateView):
    template_name = 'community_create.html'
    model = Community
    success_url = reverse_lazy('all')
    form_class = CommunityCreationForm

    def form_valid(self, form):
        community = form.save(commit=False)
        if 'private_com' in self.request.POST and self.request.POST['private_com'] == 'on':
            community.is_private = True

        community.creator = self.request.user

        community.save()
        community.subscribers.add(community.creator)
        community.save()
        return super().form_valid(form)


class AllCommunitiesView(ListView):
    template_name = 'communities_list.html'
    model = Community
    queryset = Community.objects.all()
    context_object_name = 'communities'


class PopularCommunitiesView(ListView):
    template_name = 'communities_list.html'
    model = Community
    queryset = Community.objects.annotate(num_subscribers=Count('subscribers')).order_by('-num_subscribers')
    context_object_name = 'communities'


@login_required
def my_communities(request):
    user = request.user
    communities = user.sub_communities.all()

    context = {
        'communities': communities
    }

    return render(request, 'communities_list.html', context)


class CommunityDetailView(DetailView):
    template_name = 'community_detail.html'
    model = Community
    context_object_name = 'community'

    def get_object(self, queryset=None):
        slug = self.kwargs.get('community_slug')
        return get_object_or_404(Community, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        community = self.get_object()
        context['community_posts'] = community.community_posts.all()
        return context


@login_required
def subscribe_community(request, community_slug):
    community = get_object_or_404(Community, slug=community_slug)
    user = request.user
    community.subscribers.add(user)
    community.save()
    return redirect(reverse_lazy('community_detail', kwargs={'community_slug': community_slug}))


@login_required
def unsubscribe_community(request, community_slug):
    community = get_object_or_404(Community, slug=community_slug)
    user = request.user
    community.subscribers.remove(user)
    community.save()
    return redirect(reverse_lazy('community_detail', kwargs={'community_slug': community_slug}))


@login_required
def membership(request, community_slug):
    community = get_object_or_404(Community, slug=community_slug)
    user = request.user
    if user not in community.application.all():
        community.application.add(user)
        community.save()

        mssgs.success(request, 'Ваша заявка на вступление отправлена успешно.')
    else:
        mssgs.success(request, 'вы уже подали заявку на вступление')

    return render(request, 'base.html', {'mssgs': mssgs.get_messages(request)})


# class ApllicationProcessingView(ListView):
#     template_name = 'membership.html'
#     model = Community
#     context_object_name = 'applications'
#
#     def dispatch(self, request, *args, **kwargs):
#         community = self.get_community()
#         user = request.user
#
#         if not (user.is_authenticated and user == community.creator):
#             messages.success(request, 'у вас нет прав на данное действие')
#             return render(request, 'base.html')
#
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_queryset(self):
#         community = self.get_community()
#         return community.application.all()
#
#     def get_community(self):
#         community_slug = self.kwargs['community_slug']
#         return Community.objects.get(slug=community_slug)



class ApllicationProcessingView(LoginRequiredMixin, ListView):
    template_name = 'membership.html'
    model = Community
    context_object_name = 'applications'

    def dispatch(self, request, *args, **kwargs):
        community_slug = kwargs['community_slug']
        community = get_object_or_404(Community, slug=community_slug)
        user = request.user

        if not (user.is_authenticated and user == community.creator):
            mssgs.success(request, 'у вас нет прав на данное действие')
            return render(request, 'base.html', {'mssgs': mssgs.get_messages(request)})

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        community_slug = self.kwargs['community_slug']
        community = get_object_or_404(Community, slug=community_slug)
        return community.application.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        community_slug = self.kwargs['community_slug']
        community = get_object_or_404(Community, slug=community_slug)
        context['community'] = community
        return context


class Accept(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        community_slug = kwargs['community_slug']
        user_id = kwargs['user_id']
        community = get_object_or_404(Community, slug=community_slug)
        user = get_object_or_404(User, pk=user_id)

        if self.request.user != community.creator:
            return reverse('forbidden')

        community.subscribers.add(user)

        community.application.remove(user)
        community.save()

        return reverse('application_processing', kwargs={'community_slug': community_slug})


class Decline(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        community_slug = kwargs['community_slug']
        user_id = kwargs['user_id']
        community = get_object_or_404(Community, slug=community_slug)
        user = get_object_or_404(User, pk=user_id)

        if self.request.user != community.creator:
            return reverse('forbidden')

        community.application.remove(user)
        community.save()

        return reverse('application_processing', kwargs={'community_slug': community_slug})


def forbidden(request):
    return render(request, '403.html')


class SubscribersListView(ListView):
    template_name = 'subscribers.html'
    model = User
    context_object_name = 'subscribers'

    def get_queryset(self):
        community_slug = self.kwargs['community_slug']
        community = Community.objects.get(slug=community_slug)
        return community.subscribers.all()

    def dispatch(self, request, *args, **kwargs):
        community_slug = self.kwargs['community_slug']
        community = Community.objects.get(slug=community_slug)

        if request.user not in community.subscribers.all():
            return redirect('forbidden')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        community_slug = self.kwargs['community_slug']
        community = get_object_or_404(Community, slug=community_slug)
        context['community'] = community
        context['request_user'] = self.request.user
        return context


class ExcludeUserView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        community_slug = kwargs['community_slug']
        user_id = kwargs['user_id']
        community = get_object_or_404(Community, slug=community_slug)
        user = get_object_or_404(User, pk=user_id)

        if self.request.user != community.creator:
            return reverse('forbidden')

        community.subscribers.remove(user)
        community.save()

        return reverse('subscribers', kwargs={'community_slug': community_slug})