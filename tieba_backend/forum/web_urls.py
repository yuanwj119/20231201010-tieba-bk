from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('bars/<int:bar_id>/', views.bar_detail, name='bar_detail'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/new/', views.create_post, name='post_create'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_page, name='register_page'),
]