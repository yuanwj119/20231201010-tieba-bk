from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

from .models import Category, Bar, Post, Comment
from .serializers import CategorySerializer, BarSerializer, PostSerializer, UserSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class BarViewSet(viewsets.ModelViewSet):
    queryset = Bar.objects.all().order_by('-created_at')
    serializer_class = BarSerializer
    permission_classes = [permissions.AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('bar', 'author').all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        qs = super().get_queryset()
        bar_id = self.request.query_params.get('bar')
        if bar_id:
            qs = qs.filter(bar_id=bar_id)
        return qs


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'detail': '用户名和密码必填'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'detail': '用户名已存在'}, status=400)
    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'detail': e.messages}, status=400)
    user = User.objects.create_user(username=username, password=password)
    return Response(UserSerializer(user).data, status=201)


def index(request):
    categories = Category.objects.all().order_by('name')
    selected_category = request.GET.get('category')
    bars = Bar.objects.all().order_by('-created_at')
    if selected_category:
        bars = bars.filter(category_id=selected_category)
    # 推荐热门帖子（按最后回复时间、更新时间、创建时间降序）
    hot_posts = (
        Post.objects.select_related('bar', 'author')
        .filter(Q(last_reply_at__isnull=False))
        .order_by('-last_reply_at', '-updated_at', '-created_at')[:10]
    )
    # 热门贴吧（按关注数与创建时间降序）
    hot_bars = (
        Bar.objects.select_related('category')
        .order_by('-followers', '-created_at')[:10]
    )
    return render(request, 'forum/index.html', {
        'categories': categories,
        'bars': bars,
        'hot_posts': hot_posts,
        'hot_bars': hot_bars,
        'selected_category': int(selected_category) if selected_category else None,
    })


def bar_detail(request, bar_id):
    bar = get_object_or_404(Bar, pk=bar_id)
    sort = request.GET.get('sort', 'new')
    posts = bar.posts.select_related('author').all()
    if sort == 'hot':
        posts = posts.order_by('-last_reply_at', '-updated_at')
    else:  # 'new' or others
        posts = posts.order_by('-created_at')
    return render(request, 'forum/bar_detail.html', {
        'bar': bar,
        'posts': posts,
        'sort': sort,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('bar', 'author'), pk=post_id)
    sort = request.GET.get('sort', 'new')
    comments = Comment.objects.select_related('author').filter(post=post, parent__isnull=True)
    if sort == 'hot':
        comments = comments.order_by('-likes', '-created_at')
    else:
        comments = comments.order_by('-created_at')
    # 预取子回复，用模板中循环
    comments = comments.prefetch_related('replies')
    comment_count = Comment.objects.filter(post=post).count()
    return render(request, 'forum/post_detail.html', {
        'post': post,
        'bar': post.bar,
        'comments': comments,
        'comment_count': comment_count,
        'sort': sort,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        bar_id = request.POST.get('bar_id')
        if not (title and content and bar_id):
            return render(request, 'forum/post_form.html', {
                'bars': Bar.objects.all(),
                'error': '请填写完整内容',
            })
        bar = get_object_or_404(Bar, pk=bar_id)
        Post.objects.create(bar=bar, title=title, content=content, author=request.user)
        return redirect('bar_detail', bar_id=bar.id)
    return render(request, 'forum/post_form.html', {
        'bars': Bar.objects.all(),
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
        return render(request, 'forum/login.html', {'error': '账号或密码错误'})
    return render(request, 'forum/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        if not (username and password and confirm):
            return render(request, 'forum/register.html', {'error': '请填写完整'})
        if password != confirm:
            return render(request, 'forum/register.html', {'error': '两次密码不一致'})
        if User.objects.filter(username=username).exists():
            return render(request, 'forum/register.html', {'error': '用户名已存在'})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'forum/register.html')
