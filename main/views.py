from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.views.generic import ListView
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector #allows us to search within our blog
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count



def post_list(request, tag_slug =None):

    object_list = Post.published.all()
    tag = None
    #to let users list all posts tagged with a specific tag.
    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        object_list = object_list.filter(tags__in = [tag])

    #adding pagination
    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts' : posts,
        'page' : page,
        'tag'  : tag,
    }
    return render(request, 'blog/post/list.html', context)

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year,publish__month=month, publish__day=day)

    #adding comments to each post
    comments = post.comments.filter(active =True)

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data = request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True) #returns a list of tuples with the values for the given fields. Passing flat=True to it to get single values such as [1, 2, 3, ...] instead of one-tuples such as [(1,), (2,), (3,) ...].
    
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
        .exclude(id=post.id) #get all posts that contain any of these tags, excluding the current post itself
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags','-publish')[:4] #getting the number of tags shared and ordering it by the number of tags shared and the date published

    context = {
        'post'         : post,
        'comments'     : comments,
        'comment_form' : comment_form,
        'new_comment'  : new_comment,
        'similar_posts': similar_posts
    }

    return render(request,'blog/post/detail.html', context)

def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = 'published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
        # Form fields passed validation
            cd = form.cleaned_data #assigning the form data into a variable cd
        # ... send email
        post_url      = request.build_absolute_uri(post.get_absolute_url())
        subject       = f"{cd['name']} recommends you read " \
        f"{post.title}"
        message       = f"Read {post.title} at {post_url}\n\n" \
        f"{cd['name']}\'s comments: {cd['comments']}"
        email_from     = 'sirdesmond09@gmail.com'
        recipient_list = [cd['to']]
        
        send_mail(subject, message, email_from, recipient_list)
        sent = True
    else:
        form = EmailPostForm()
        

    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }
    return render(request, 'blog/post/share.html', context)

def post_search(request):
    form    = SearchForm
    query   = None
    results = []

    if 'query' in request.GET:
        form =SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + \
                            SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(search= search_vector, rank = SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')

    context = {
            'results': results,
            'form': form,
            'query': query,
        }
    return render(request, 'blog/post/search.html', context)
