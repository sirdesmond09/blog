from django.urls import path
from .views import post_detail, post_list, post_share #PostList

app_name = 'main'
urlpatterns = [

    path('', post_list, name='post_list'),
    path('tag/<slug:tag_slug>/',post_list, name='post_list_by_tag'),
    # path('', PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', post_detail, name='post_detail'),
    path('<int:post_id>/share/', post_share, name = 'post_share'),
]