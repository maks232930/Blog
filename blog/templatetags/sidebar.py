import datetime

from django import template
from django.db.models import F, Count

from blog.models import Post, Category, Tag

register = template.Library()


@register.inclusion_tag('blog/recent_post_tpl.html')
def get_recent_posts():
    posts = Post.objects.filter(published_date__lte=datetime.datetime.today(), published=True)[:3] \
        .select_related('category', 'author') \
        .prefetch_related('tags')
    return {'posts': posts}


@register.inclusion_tag('blog/category_tpl.html')
def get_categories():
    categories = Category.objects.annotate(cnt=Count('post', filter=F('post__published'))).filter(
        cnt__gt=0,
        post__published_date__lte=datetime.datetime.today())
    return {'categories': categories}


@register.inclusion_tag('blog/tag_tpl.html')
def get_tags():
    tags = Tag.objects.annotate(cnt=Count('post', filter=F('post__published'))).filter(
        cnt__gt=0,
        post__published_date__lte=datetime.datetime.today())
    return {'tags': tags}
