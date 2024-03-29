from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_GET
from django.core.cache import cache

from .forms import CommentForm, PostForm
from .models import Follow, Post, Group, User


@require_GET
def index(request):
    posts = cache.get('posts:index')
    if posts is None:
        posts = Post.objects.select_related('group').all()
        cache.set('posts:index', posts, timeout=20)

    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page_obj')
    page = paginator.get_page(page_number)

    return render(request, 'posts/index.html', {'page_obj': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post = group.posts.all()
    paginator = Paginator(post, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page_obj')
    page = paginator.get_page(page_number)

    return render(
        request,
        'posts/group_list.html',
        {'group': group, 'page_obj': page}
    )


def post_detail(request, post_id, username=None):
    post_detail = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post_detail.comments.all()

    posts_count = post_detail.author.posts.count()
    followers_count = Follow.objects.count()

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=post_detail.author).exists()

    context = {
        'form': form,
        'post_detail': post_detail,
        'posts_count': posts_count,
        'comments': comments,
        'followers_count': followers_count,
        'following': following,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', username, post_id)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', post.author.username)

    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        post.save()

        return redirect('posts:post_detail', post.id)

    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post_edit': post}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)

    paginator = Paginator(author.posts.all(), settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page_obj')
    page = paginator.get_page(page_number)

    posts_count = author.posts.count()
    followers_count = Follow.objects.count()

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()

    context = {
        'author': author,
        'posts_count': posts_count,
        'page_obj': page,
        'followers_count': followers_count,
        'following': following,
    }

    return render(request, 'posts/profile.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page_obj')
    page = paginator.get_page(page_number)

    return render(request, "posts/follow.html", {'page_obj': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    if request.user != author:
        Follow.objects.get_or_create(
            author=author,
            user=request.user
        )

    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(author=author, user=request.user).delete()

    return redirect('posts:profile', username)
