import os
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from forum.models import Category, Bar, Post, Comment

class Command(BaseCommand):
    help = 'Render pages to static HTML files: index, all bars, and all posts.'

    def handle(self, *args, **options):
        base_dir = str(settings.BASE_DIR)
        out_dir = os.path.join(base_dir, 'static_site')
        os.makedirs(out_dir, exist_ok=True)

        factory = RequestFactory()
        dummy_request = factory.get('/')
        dummy_request.user = AnonymousUser()

        # Export index page
        categories = Category.objects.all().order_by('name')
        bars = Bar.objects.all().order_by('-created_at')
        hot_posts = (
            Post.objects.select_related('bar', 'author')
            .filter(Q(last_reply_at__isnull=False))
            .order_by('-last_reply_at', '-updated_at', '-created_at')[:10]
        )
        hot_bars = (
            Bar.objects.select_related('category')
            .order_by('-followers', '-created_at')[:10]
        )
        index_ctx = {
            'categories': categories,
            'bars': bars,
            'hot_posts': hot_posts,
            'hot_bars': hot_bars,
            'selected_category': None,
            'request': dummy_request,
        }
        index_html = render_to_string('forum/index.html', index_ctx, request=dummy_request)
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        self.stdout.write(self.style.SUCCESS('Exported index.html'))

        # Export bar pages
        bars_dir = os.path.join(out_dir, 'bars')
        os.makedirs(bars_dir, exist_ok=True)
        count_bar = 0
        for bar in Bar.objects.all():
            posts = bar.posts.select_related('author').all().order_by('-created_at')
            ctx = {
                'bar': bar,
                'posts': posts,
                'sort': 'new',
                'request': dummy_request,
            }
            html = render_to_string('forum/bar_detail.html', ctx, request=dummy_request)
            out_path = os.path.join(bars_dir, f'{bar.id}.html')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            count_bar += 1
        self.stdout.write(self.style.SUCCESS(f'Exported {count_bar} bar pages'))

        # Export post pages
        posts_dir = os.path.join(out_dir, 'posts')
        os.makedirs(posts_dir, exist_ok=True)
        count_post = 0
        for post in Post.objects.select_related('bar', 'author').all():
            comments = Comment.objects.select_related('author').filter(post=post, parent__isnull=True).order_by('-created_at').prefetch_related('replies')
            ctx = {
                'post': post,
                'bar': post.bar,
                'comments': comments,
                'comment_count': Comment.objects.filter(post=post).count(),
                'sort': 'new',
                'request': dummy_request,
            }
            html = render_to_string('forum/post_detail.html', ctx, request=dummy_request)
            out_path = os.path.join(posts_dir, f'{post.id}.html')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html)
            count_post += 1
        self.stdout.write(self.style.SUCCESS(f'Exported {count_post} post pages'))

        self.stdout.write(self.style.SUCCESS(f'Done. Output: {out_dir}'))