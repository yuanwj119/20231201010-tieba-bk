# Django 贴吧风格项目作业对照说明

## 项目概述
- 本项目实现一个简易“贴吧/论坛”系统，包含首页、吧详情页、帖子详情页、发帖页、登录/注册页。
- 后端：Django + Django REST Framework（部分接口）。
- 前端：Django 模板（`base.html` + 各页面模板）+ 自定义 CSS，含移动端适配。
- 数据：提供种子脚本 `seed_tieba` 批量生成演示数据（吧、帖子、评论）。
- 额外：提供 `export_html` 命令导出静态站点 HTML 以便演示与提交。

## 核心 Django 组件（符合“基本要求”）
- 模型：`Category`、`Bar`、`Post`、`Comment`（见下文字段）。
- 视图与路由（`forum/web_urls.py`）：
  - `/` → `index`（首页）
  - `/bars/<bar_id>/` → `bar_detail`（吧页/帖子列表，支持最新/最热）
  - `/posts/<post_id>/` → `post_detail`（帖子详情/评论树）
  - `/posts/new/` → `create_post`（发布新帖）
  - `/login/`、`/logout/`、`/register/`（认证相关）
- 接口（`forum/urls.py`）：`/api/categories`、`/api/bars`、`/api/posts`、`/api/register`。

## 数据模型设计（符合“数据模型结构”）
- `Category(name, slug)`：分类。
- `Bar(name, description, cover_url, followers, category(FK), created_at)`：贴吧。
- `Post(title, content, author(FK User), bar(FK), created_at, updated_at, last_reply_at)`：帖子。
- `Comment(post(FK), author(FK), content, likes, parent(self FK, 可空), created_at)`：评论（支持楼中楼）。

## 视图功能清单（与“列表/详情/创建/编辑页”对照）
- 列表页：吧详情页展示本吧帖子列表（最新/最热）。
- 详情页：帖子详情页展示正文与评论树；吧页展示吧信息与帖子列表；首页展示推荐/热门。
- 创建页：`/posts/new/` 发帖页（含选择吧、标题、内容、发布设置）。
- 编辑页：尚未实现（可快速补充一个 `/posts/<id>/edit/` 页，沿用发帖模板逻辑）。

## 前端展示与模板结构（符合“模板层结构与交互”）
- 统一布局：`forum/base.html` 顶部导航 + 容器 + 页脚。
- 页面模板：`index.html`、`bar_detail.html`、`post_detail.html`、`post_form.html`、`login.html`、`register.html`。
- 样式：`static/css/tieba.css`，含首页轮播、两栏布局、吧页、帖详情、评论区、表单与移动端样式。
- 交互占位：评论发送/关注/收藏/分享/预览等按钮已布置，占位待接入后端逻辑。
- 如需严格使用前端框架（Vue/React）：可在模板中以 CDN 引入 Vue，实现评论排序/搜索等组件的前端交互；该项为可选增强。

## 作业提交建议（符合“学习总结、需求分析、模块内容、ER 图”）
- 需求分析：社区讨论核心流程（浏览→选择吧→发帖→看帖→评论）。
- 模块内容：模型与视图映射、模板结构、样式与交互说明（本 README 可做基础）。
- E-R 图：见 `docs/ER.md`（ASCII/Markdown 表示）。
- 过程截图：建议包含首页、吧页、帖子详情、发帖页、登录/注册页，以及静态导出目录截图。
- 代码示例：可选取“帖子详情页”功能，展示视图获取数据→模板渲染→评论树结构的调用流程。

## 静态导出（便于提交与验收）
- 运行：`python manage.py export_html`
- 输出目录：`tieba_backend/static_site/`（首页 `index.html`、`bars/<id>.html`、`posts/<id>.html`）。

## 与老师要求的差距与补充计划
- 编辑页未实现：补充 `edit_post` 视图与 `post_edit.html` 模板（预计 <1h）。
- 前端框架要求（Vue/React）如需满足：以 CDN 引入 Vue，在吧页实现“搜索/筛选/分页”的前端交互（预计 <1h 做基础版）。
- 评论提交与收藏/分享等交互当前为占位：可根据时间接入后端接口。

## 快速补充方案（若需要我可立即实现）
1. 新增路由：`/posts/<post_id>/edit/`（仅作者可编辑）。
2. 复用发帖模板，预填标题与内容，提交后回帖详情或吧页。
3. 在 `bar_detail.html` 的每条帖子后添加“编辑”占位链接（登录且为作者时显示）。