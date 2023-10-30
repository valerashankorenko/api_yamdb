from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    GetTokenViewSet, RegisterViewSet, ReviewViewSet,
                    TitleViewSet, UserViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register('titles/(?P<title_id>\\d+)/reviews/('
                '?P<review_id>\\d+)/comments',
                CommentViewSet, basename='comment')
router.register('titles/(?P<title_id>\\d+)/reviews',
                ReviewViewSet, basename='review')

urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/auth/signup/',
        RegisterViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        'v1/auth/token/',
        GetTokenViewSet.as_view({'post': 'create'}),
        name='token'
    ),
]
