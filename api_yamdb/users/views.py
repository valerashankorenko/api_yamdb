from rest_framework import filters, permissions, viewsets

from .mixins import GetTokenMixin, UserModelMixin, UserRegisterMixin
from .models import User
from .permissions import (
    IsAdmin,
)
from .serializers import (
    TokenSerializer, UserRegisterSerializer, UserSerializer
)


class UserViewSet(UserModelMixin, viewsets.GenericViewSet):
    """
    Вьюсет для для работы с моделью - User.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class RegisterViewSet(UserRegisterMixin, viewsets.GenericViewSet):
    """
    Вьюсет для для регистрации новых пользователей.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)


class GetTokenViewSet(GetTokenMixin, viewsets.GenericViewSet):
    """
    Вьюсет для получения JWT токена.
    """
    queryset = User.objects.all()
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)
