import datetime

from django.db.models import F
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from .forms import CommentForm
from .models import *


class HomeListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.prefetch_related('tags') \
                   .filter(published=True, published_date__lte=datetime.datetime.today())[:6] \
            .select_related('category', 'author')


class AllPostsListView(ListView):
    model = Post
    template_name = 'blog/list_all_posts.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(published=True, published_date__lte=datetime.datetime.today()) \
            .select_related('category', 'author') \
            .prefetch_related('tags')


class PostDetailView(FormMixin, DetailView):
    queryset = Post.objects.prefetch_related('tags').select_related('author')
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all()
        context['form'] = CommentForm(initial={'post': self.object})
        self.object.views = F('views') + 1
        self.object.save()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super(PostDetailView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        if kwargs != None:
            return reverse_lazy('post_detail', kwargs={'slug': self.kwargs['slug']})
        else:
            return reverse_lazy('post_detail', args=(self.object.slug,))


class PostsByCategory(ListView):
    model = Post
    template_name = 'blog/views_posts_by_category.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Post.objects.filter(category__slug=self.kwargs['slug']) \
            .select_related('category',
                            'author').prefetch_related('tags').first()
        return context

    def get_queryset(self):
        return Post.objects.filter(published=True, category__slug=self.kwargs['slug'],
                                   published_date__lte=datetime.datetime.today()) \
            .select_related('category', 'author') \
            .prefetch_related('tags')


class PostsByTag(ListView):
    model = Post
    template_name = 'blog/views_posts_by_tag.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = Post.objects.filter(tags__slug=self.kwargs['slug']) \
            .select_related('category', 'author') \
            .prefetch_related('tags') \
            .first()
        return context

    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs['slug'], published=True,
                                   published_date__lte=datetime.datetime.today()) \
            .select_related('category', 'author') \
            .prefetch_related('tags')


class Search(ListView):
    model = Post
    template_name = 'blog/search_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['s'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Post.objects.filter(title__icontains=query, published=True,
                                          published_date__lte=datetime.datetime.today()) \
            .select_related('category', 'author') \
            .prefetch_related('tags')
        return object_list
