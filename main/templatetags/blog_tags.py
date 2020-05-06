''' Creating my custom template tags. Django provides the following helper functions 
that allow you to create your own template tags in an easy manner: 

1. simple_tag: Processes the data and returns a string
2. inclusion_tag: Processes the data and returns a rendered template '''

from django import template
from main.models import Post

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

    