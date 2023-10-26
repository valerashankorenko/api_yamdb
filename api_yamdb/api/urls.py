from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet

router = DefaultRouter()
router.register('titles/(?P<title_id>\\d+)/reviews/('
                '?P<review_id>\\d+)/comments',
                CommentViewSet, basename='comment')
router.register('titles/(?P<title_id>\\d+)/reviews',
                ReviewViewSet, basename='review')

urlpatterns = [
    path('v1/', include(router.urls)),
]
