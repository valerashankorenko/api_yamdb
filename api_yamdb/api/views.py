from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Comment, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import (CategoryGenreMixin, GetTokenMixin, UserModelMixin,
                     UserRegisterMixin)
from .permissions import (IsAdminOrReadOnly, IsAuthenticatedAdmin,
                          IsModeratorOrAdminOrAuthor)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadOnlySerializer, TitleSerializer,
                          TokenSerializer, UserRegisterSerializer,
                          UserSerializer)


class UserViewSet(UserModelMixin,
                  viewsets.GenericViewSet):
    """
    Вьюсет для для работы с моделью - User.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class RegisterViewSet(UserRegisterMixin,
                      viewsets.GenericViewSet):
    """
    Вьюсет для для регистрации новых пользователей.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)


class GetTokenViewSet(GetTokenMixin,
                      viewsets.GenericViewSet):
    """
    Вьюсет для получения JWT токена.
    """
    queryset = User.objects.all()
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)


class CategoryViewSet(CategoryGenreMixin,
                      viewsets.GenericViewSet):
    """
    Вьюсет для Category.
    """
    queryset = Category.objects.order_by('id')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CategoryGenreMixin,
                   viewsets.GenericViewSet):
    """
    Вьюсет для Genre.
    """
    queryset = Genre.objects.order_by('id')
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
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')
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
    Вьюсет для работы с моделью - Review.

    Параметры:
        - Включает CRUD-операции, связь с объектами Tile.
        - Необходимо указать title_id в URL для работы с отзывами:
        /titles/{title_id}/reviews/.
    """
    queryset = Review.objects.order_by('id')
    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsModeratorOrAdminOrAuthor,)
    lookup_field = 'pk'
    lookup_url_kwarg = 'review_id'

    def get_title(self):
        """
        Метод возвращает объект Title, соответствующий title_id из URL.
        Вызывает 404 ошибку, если объект не найден.
        """
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """
        Метод возвращает queryset отзывов, отфильтрованных по
        id произведения и отсортированных по id отзывов.
        """
        return self.queryset.filter(title_id=self.get_title())

    def perform_create(self, serializer):
        """
        Метод устанавливает автора при создании отзыва.
        """
        serializer.save(author=self.request.user, title=self.get_title())

    def get_object(self):
        """
        Метод возвращает отдельный отзыв, связанный
        с произведением, указанным в параметрах запроса.
        """
        obj = get_object_or_404(
            self.get_queryset(),
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'))

        if obj.title_id != self.get_title().id:
            raise PermissionDenied('Несоответствие title_id и review_id')

        self.check_object_permissions(self.request, obj)
        return obj


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с моделью - Comment.

    Параметры:
        - Включает CRUD-операции, связь с объектами Review.
        - Необходимо указать title_id и review_id в URL для работы с
        комментариями: /titles/{title_id}/reviews/{review_id}/comments/.
    """
    queryset = Comment.objects.order_by('id')
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsModeratorOrAdminOrAuthor,)
    lookup_field = 'pk'
    lookup_url_kwarg = 'comment_id'

    def perform_create(self, serializer):
        """
        Метод устанавливает автора при создании комментария.
        """
        review = get_object_or_404(
            Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
