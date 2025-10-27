from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Category, Bar, Post, Comment
from django.utils.text import slugify
from random import randint, choice
from django.utils import timezone
from datetime import timedelta

CATS = [
    ('游戏', 'game'), ('美食', 'food'), ('学习', 'study'), ('科技', 'tech'), ('影视', 'movie')
]
BARS = {
    'game': ['王者荣耀', '英雄联盟', '原神', 'CSGO'],
    'food': ['川菜', '甜点', '火锅', '烧烤'],
    'study': ['考研', '英语学习', '编程', '读书'],
    'tech': ['数码', 'AI', 'Python', '前端'],
    'movie': ['科幻片', '动漫', '国产剧', '欧美剧'],
}

POST_TITLES = [
    '新人报到，求带飞',
    '今天吃什么好？',
    '学习打卡第1天',
    '有推荐的装备吗',
    '这集真不错！',
]

# 供“发新帖内容演示”使用的示例帖
EXAMPLE_POSTS = [
    (
        '演示：图文混排',
        "大家好！这里是图文混排演示 😊\n\n- 列表项 A\n- 列表项 B\n\n[图片占位] https://picsum.photos/seed/tieba/800/400\n\n欢迎补充话题，@所有吧友！",
    ),
    (
        '演示：附图',
        "分享一张相关图片：\n\n图片链接：https://picsum.photos/seed/bar/640/360\n\n欢迎讨论！",
    ),
    (
        '演示：视频占位',
        "视频外链占位：https://example.com/video.mp4\n\n（实际项目可接入上传/外链播放组件）",
    ),
    (
        '演示：Markdown代码',
        "下面是代码片段：\n\n```python\nprint('Hello Tieba')\nfor i in range(3):\n    print(i)\n```\n\n欢迎补充讨论。",
    ),
]

COMMENTS = [
    '支持一下，写得不错！',
    '顶起来～',
    '我也有同样的疑问。',
    '这张图很赞！',
    '有相关资料链接吗？',
]
REPLIES = [
    '赞同你的观点',
    '可以参考官方文档',
    '谢谢回复',
    '哈哈哈，说得对',
]


def ensure_examples(bar, user):
    created = 0
    for title, content in EXAMPLE_POSTS:
        if not Post.objects.filter(bar=bar, title=title).exists():
            Post.objects.create(
                bar=bar,
                title=title,
                author=user,
                content=content,
                last_reply_at=timezone.now() - timedelta(minutes=randint(0, 90)),
            )
            created += 1
    return created


def seed_comments_for_post(post, user):
    # 若已有评论则不重复生成
    if Comment.objects.filter(post=post).exists():
        return 0
    made = 0
    top_count = randint(2, 4)
    for i in range(top_count):
        c = Comment.objects.create(
            post=post,
            author=user,
            content=f"{choice(COMMENTS)}（演示）",
            likes=randint(0, 20),
            created_at=timezone.now() - timedelta(minutes=randint(5, 200)),
        )
        made += 1
        # 子回复
        for j in range(randint(1, 2)):
            Comment.objects.create(
                post=post,
                author=user,
                content=f"{choice(REPLIES)}（演示回复）",
                likes=randint(0, 10),
                parent=c,
                created_at=timezone.now() - timedelta(minutes=randint(1, 100)),
            )
            made += 1
    return made


class Command(BaseCommand):
    help = 'Seed Tieba-style demo data: categories, bars, posts, comments, and a demo user.'

    def handle(self, *args, **kwargs):
        # Create demo user
        user, created = User.objects.get_or_create(username='demo')
        if created:
            user.set_password('demo12345')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created user demo / demo12345'))
        else:
            self.stdout.write('User demo already exists')

        # Create categories
        cat_map = {}
        for name, key in CATS:
            cat, _ = Category.objects.get_or_create(name=name, slug=key)
            cat_map[key] = cat
        self.stdout.write(self.style.SUCCESS(f'Ensured {len(cat_map)} categories'))

        # Create bars per category
        bar_count = 0
        for key, names in BARS.items():
            cat = cat_map[key]
            for n in names:
                bar, _ = Bar.objects.get_or_create(
                    name=n,
                    defaults={
                        'description': f'{n} 吧的简介占位',
                        'cover_url': '',
                        'category': cat,
                        'followers': randint(100, 5000),
                    },
                )
                # Ensure category set if existed without it
                if not bar.category_id:
                    bar.category = cat
                    bar.save()
                bar_count += 1
        self.stdout.write(self.style.SUCCESS(f'Ensured {bar_count} bars'))

        # Create posts for each bar（基础帖）
        post_created = 0
        for bar in Bar.objects.all():
            existing = bar.posts.count()
            to_make = max(0, 5 - existing)
            for i in range(to_make):
                title = f'{choice(POST_TITLES)} · {i+1}'
                p = Post.objects.create(
                    bar=bar,
                    title=title,
                    author=user,
                    content=f'{bar.name} 讨论帖内容占位：{title}\n\n包含文字、表情 😊，以及可扩展的图片/视频占位。',
                    last_reply_at=timezone.now() - timedelta(minutes=randint(5, 120)),
                )
                post_created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {post_created} base posts'))

        # Ensure example posts for each bar（演示帖）
        example_total = 0
        for bar in Bar.objects.all():
            example_total += ensure_examples(bar, user)
        self.stdout.write(self.style.SUCCESS(f'Ensured {example_total} example posts'))

        # 为每个帖子生成评论与子回复
        comment_total = 0
        for p in Post.objects.all():
            comment_total += seed_comments_for_post(p, user)
        self.stdout.write(self.style.SUCCESS(f'Ensured {comment_total} comments & replies'))

        self.stdout.write(self.style.SUCCESS('Seeding finished.'))