from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Comment, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import (GetTokenMixin, ListCreatDestroyViewSet,
                     UserModelMixin, UserRegisterMixin)
from .permissions import IsAdmin, IsOwner, IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleSerializer,
                          TitleReadOnlySerializer, TokenSerializer,
                          UserRegisterSerializer, UserSerializer)


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


class CategoryViewSet(ListCreatDestroyViewSet):
    """
    Вьюсет для Category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreatDestroyViewSet):
    """
    Вьюсет для Genre.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для Title.
    Подсчитывает рейтинг для каждого произведения.
    """
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """
        Выбор Serializer при безопасных методах и нет.
        """
        if self.request.method == 'GET':
            return TitleReadOnlySerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с объектами Review.

    Параметры:
        - Включает CRUD-операции, связь с объектами Title.
        - Необходимо указать title_id в URL для работы с отзывами:
        /titles/{title_id}/reviews/.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (permissions.AllowAny,)

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от метода запроса.
        """
        if self.request.method == 'GET':
            return (permissions.AllowAny(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ['PATCH', 'DELETE']:
            return (IsAdmin(), IsOwner(),)
        else:
            return super().get_permissions()

    def get_queryset(self):
        """
        Возвращает отфильтрованный QuerySet отзывов для конкретного title.
        """
        title_id = self.kwargs['title_id']
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        """
        Устанавливает автора при создании отзыва.
        """
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)

    lookup_field = 'pk'
    lookup_url_kwarg = 'review_id'


class CommentViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с объектами Comment.

    Параметры:
        - Включает CRUD-операции, связь с объектами Review.
        - Необходимо указать title_id и review_id в URL для работы с
        комментариями: /titles/{title_id}/reviews/{review_id}/comments/.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.AllowAny,)

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от метода запроса.
        """
        if self.request.method == 'GET':
            return (permissions.AllowAny(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ['PATCH', 'DELETE']:
            return (IsAdmin(), IsOwner(),)
        else:
            return super().get_permissions()

    def get_queryset(self):
        """
        Возвращает отфильтрованный QuerySet комментариев для конкретного
        title и review.
        """
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']
        return Comment.objects.filter(review__title_id=title_id,
                                      review_id=review_id)

    def perform_create(self, serializer):
        """
        Устанавливает автора при создании комментария.
        """
        review_id = self.kwargs.get('review_id')
        review = self.__get_post(review_id)
        serializer.save(author=self.request.user, review=review)

    lookup_field = 'pk'
    lookup_url_kwarg = 'comment_id'
