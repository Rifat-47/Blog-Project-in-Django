from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Category, Post, ReadPost, SavedPost, SiteSettings, Tag


def _paginate(request, queryset, per_page=None):
    if per_page is None:
        per_page = SiteSettings.get_solo().posts_per_page
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def _sidebar_context():
    return {
        'sidebar_categories': Category.objects.all(),
        'sidebar_recent': Post.objects.filter(
            status=Post.STATUS_PUBLISHED
        ).select_related('author')[:5],
    }


def _reading_sets(user):
    """Return sets of post IDs the user has read/saved. Empty sets for anonymous."""
    if not user.is_authenticated:
        return set(), set()
    read_ids = set(ReadPost.objects.filter(user=user).values_list('post_id', flat=True))
    saved_ids = set(SavedPost.objects.filter(user=user).values_list('post_id', flat=True))
    return read_ids, saved_ids


# ── Public views ──────────────────────────────────────────

def home(request):
    posts = Post.objects.filter(
        status=Post.STATUS_PUBLISHED
    ).select_related('author', 'author__profile', 'category')

    # Homepage filter for authenticated users
    active_filter = request.GET.get('filter', 'all')
    read_ids, saved_ids = _reading_sets(request.user)

    if request.user.is_authenticated:
        if active_filter == 'unread':
            posts = posts.exclude(id__in=read_ids)
        elif active_filter == 'read':
            posts = posts.filter(id__in=read_ids)
        elif active_filter == 'saved':
            posts = posts.filter(id__in=saved_ids)

    context = {
        'page_obj': _paginate(request, posts),
        'title': 'Home',
        'active_filter': active_filter,
        'read_ids': read_ids,
        'saved_ids': saved_ids,
    }
    context.update(_sidebar_context())
    return render(request, 'blog/home.html', context)


def about(request):
    return render(request, 'blog/about.html', {'title': 'About', 'settings': SiteSettings.get_solo()})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.status == Post.STATUS_DRAFT and post.author != request.user:
        raise Http404

    is_read = False
    is_saved = False
    if request.user.is_authenticated:
        is_read = ReadPost.objects.filter(user=request.user, post=post).exists()
        is_saved = SavedPost.objects.filter(user=request.user, post=post).exists()

    context = {
        'post': post,
        'title': post.title,
        'is_read': is_read,
        'is_saved': is_saved,
    }
    context.update(_sidebar_context())
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        status=Post.STATUS_PUBLISHED, category=category
    ).select_related('author', 'author__profile', 'category')
    read_ids, saved_ids = _reading_sets(request.user)
    context = {
        'page_obj': _paginate(request, posts),
        'title': f'Category: {category.name}',
        'filter_label': category.name,
        'filter_icon': 'bi-folder2-open',
        'read_ids': read_ids,
        'saved_ids': saved_ids,
    }
    context.update(_sidebar_context())
    return render(request, 'blog/post_list_filtered.html', context)


def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(
        status=Post.STATUS_PUBLISHED, tags=tag
    ).select_related('author', 'author__profile', 'category')
    read_ids, saved_ids = _reading_sets(request.user)
    context = {
        'page_obj': _paginate(request, posts),
        'title': f'Tag: #{tag.name}',
        'filter_label': f'#{tag.name}',
        'filter_icon': 'bi-tag',
        'read_ids': read_ids,
        'saved_ids': saved_ids,
    }
    context.update(_sidebar_context())
    return render(request, 'blog/post_list_filtered.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    posts = Post.objects.none()
    if query:
        posts = Post.objects.filter(
            status=Post.STATUS_PUBLISHED
        ).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'author__profile', 'category').distinct()
    read_ids, saved_ids = _reading_sets(request.user)
    context = {
        'page_obj': _paginate(request, posts),
        'title': f'Search: {query}' if query else 'Search',
        'query': query,
        'filter_label': f'Results for "{query}"' if query else 'Search',
        'filter_icon': 'bi-search',
        'read_ids': read_ids,
        'saved_ids': saved_ids,
    }
    context.update(_sidebar_context())
    return render(request, 'blog/post_list_filtered.html', context)


# ── Reading list ──────────────────────────────────────────

@login_required
def reading_list(request):
    tab = request.GET.get('tab', 'saved')
    cat_slug = request.GET.get('category', '')
    tag_slug = request.GET.get('tag', '')
    status_filter = request.GET.get('status', 'all')

    all_categories = Category.objects.all()
    all_tags = Tag.objects.all()

    if tab == 'read':
        posts = Post.objects.filter(
            status=Post.STATUS_PUBLISHED,
            read_by__user=request.user,
        ).select_related('author', 'author__profile', 'category').order_by('-read_by__read_at')
    else:
        tab = 'saved'
        posts = Post.objects.filter(
            status=Post.STATUS_PUBLISHED,
            saved_by__user=request.user,
        ).select_related('author', 'author__profile', 'category').order_by('-saved_by__saved_at')

        # Status sub-filter (only on saved tab)
        if status_filter == 'read':
            read_ids = set(ReadPost.objects.filter(user=request.user).values_list('post_id', flat=True))
            posts = posts.filter(id__in=read_ids)
        elif status_filter == 'unread':
            read_ids = set(ReadPost.objects.filter(user=request.user).values_list('post_id', flat=True))
            posts = posts.exclude(id__in=read_ids)

    # Category filter
    active_category = None
    if cat_slug:
        active_category = Category.objects.filter(slug=cat_slug).first()
        if active_category:
            posts = posts.filter(category=active_category)

    # Tag filter
    active_tag = None
    if tag_slug:
        active_tag = Tag.objects.filter(slug=tag_slug).first()
        if active_tag:
            posts = posts.filter(tags=active_tag)

    read_ids, saved_ids = _reading_sets(request.user)

    context = {
        'page_obj': _paginate(request, posts),
        'title': 'Reading List',
        'tab': tab,
        'status_filter': status_filter,
        'all_categories': all_categories,
        'all_tags': all_tags,
        'active_category': active_category,
        'active_tag': active_tag,
        'cat_slug': cat_slug,
        'tag_slug': tag_slug,
        'read_ids': read_ids,
        'saved_ids': saved_ids,
        'read_count': ReadPost.objects.filter(user=request.user).count(),
        'saved_count': SavedPost.objects.filter(user=request.user).count(),
    }
    context.update(_sidebar_context())
    return render(request, 'blog/reading_list.html', context)


# ── AJAX toggle views ─────────────────────────────────────

@login_required
@require_POST
def toggle_read(request, slug):
    post = get_object_or_404(Post, slug=slug)
    obj, created = ReadPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'unread'})
    return JsonResponse({'status': 'read'})


@login_required
@require_POST
def toggle_save(request, slug):
    post = get_object_or_404(Post, slug=slug)
    obj, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'unsaved', 'saved_count': SavedPost.objects.filter(user=request.user).count()})
    return JsonResponse({'status': 'saved', 'saved_count': SavedPost.objects.filter(user=request.user).count()})


# ── Post CRUD ─────────────────────────────────────────────

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been created!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Post'
        context['legend'] = 'Create Post'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been updated!')
        return super().form_valid(form)

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Post'
        context['legend'] = 'Update Post'
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog-home')

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your post has been deleted.')
        return super().form_valid(form)
