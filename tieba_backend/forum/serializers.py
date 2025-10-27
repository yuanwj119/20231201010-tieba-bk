from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Bar, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at']


class BarSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), write_only=True
    )

    class Meta:
        model = Bar
        fields = ['id', 'name', 'description', 'cover_url', 'followers', 'created_at', 'category', 'category_id']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(source='author', queryset=User.objects.all(), write_only=True)
    bar = BarSerializer(read_only=True)
    bar_id = serializers.PrimaryKeyRelatedField(source='bar', queryset=Bar.objects.all(), write_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at', 'last_reply_at',
            'author', 'author_id', 'bar', 'bar_id'
        ]