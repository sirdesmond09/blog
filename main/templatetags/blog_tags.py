''' Creating my custom template tags. Django provides the following helper functions 
that allow you to create your own template tags in an easy manner: 

1. simple_tag: Processes the data and returns a string
2. inclusion_tag: Processes the data and returns a rendered template 
3. filter: This is used for registering custom filters'''

from django import template
from main.models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown


register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    context = {
        'latest_posts': latest_posts
    }
    return(context)

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))