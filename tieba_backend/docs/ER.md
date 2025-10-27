# 项目 E-R（实体关系）示意

```
User (Django auth_user)
- id
- username
- password
- email
- date_joined

Category
- id
- name
- slug

Bar
- id
- name
- description
- cover_url
- followers (int)
- category_id (FK → Category.id)
- created_at

Post
- id
- title
- content (Text)
- author_id (FK → User.id)
- bar_id (FK → Bar.id)
- created_at
- updated_at
- last_reply_at

Comment
- id
- post_id (FK → Post.id)
- author_id (FK → User.id)
- content (Text)
- likes (int)
- parent_id (FK → Comment.id, NULL 可表示一级评论)
- created_at
```

关系说明：
- Category 1 — N Bar：一个分类下有多个贴吧。
- Bar 1 — N Post：一个吧下有多个帖子。
- Post 1 — N Comment：一个帖子有多条评论。
- User 1 — N Post / 1 — N Comment：用户可发布多帖与多条评论。
- Comment N — 1 Comment（parent）：支持楼中楼（可空）。

页面与实体对应：
- 首页（`/`）：聚合 Bar/Post 的精选信息。
- 吧详情（`/bars/<id>/`）：围绕 Bar 展示 Post 列表与吧信息。
- 帖子详情（`/posts/<id>/`）：围绕 Post 展示正文与 Comment 树。
- 发帖页（`/posts/new/`）：创建 Post。
- 计划补充：编辑页（`/posts/<id>/edit/`）。