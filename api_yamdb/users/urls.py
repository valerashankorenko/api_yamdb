from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (GetTokenViewSet, RegisterViewSet, UserViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

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
    )
]
