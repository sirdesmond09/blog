"""
Django has a built-in syndication feed framework that you can use to dynamically
generate RSS or Atom feeds in a similar manner to creating sitemaps using the
site's framework. A web feed is a data format (usually XML) that provides users
with the most recently updated content. Users will be able to subscribe to your
feed using a feed aggregator (software that is used to read feeds and get new content
notifications)."""


from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from .models import Post

class LatestPostsFeed(Feed):
    title = 'My blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of my blog.'
    
    def items(self):
        return Post.published.all()[:5]
    def item_title(self, item):
        return item.title
    def item_description(self, item):
        return truncatewords(item.body, 30)
