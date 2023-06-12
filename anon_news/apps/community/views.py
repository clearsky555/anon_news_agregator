from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from apps.community.forms import CommunityCreationForm
from apps.community.models import Community


# Create your views here.
class CommunityCreateView(CreateView):
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