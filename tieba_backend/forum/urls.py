from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BarViewSet, PostViewSet, register

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'bars', BarViewSet)
router.register(r'posts', PostViewSet)

urlpatterns = [
    path('register/', register, name='register'),
    path('', include(router.urls)),
]