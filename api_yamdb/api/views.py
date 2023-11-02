from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsModeratorOrAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadOnlySerializer, TitleSerializer,
                          TokenSerializer, UserRegisterSerializer,
                          UserSerializer)


class UserViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Вьюсет для для работы с моделью - User.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get', 'patch', 'delete'],
        detail=False,
        url_path=r'(?P<username>[\w.@+-]+)',
        serializer_class=UserSerializer,
    )
    def get_user_profile(self, request, username):
        """
        Метод реализует:
        - получение данных о пользователе, их редактирование или удаление.
        """
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_own_profile(self, request):
        """
        Метод реализует:
        - получение пользователем данных о себе и их редактирование.
        """
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Вьюсет для для регистрация новых пользователей.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """
        Метод реализует:
        - создание нового пользователя,
        - отправку на его почту - кода подтверждения.
        """
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(
                **serializer.validated_data
            )
        except IntegrityError:
            # обработка исключения,
            # вызванного дублированием одного из ключевых полей
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            if User.objects.filter(email=email).exists():
                err_value = f'email - {email}'
            if User.objects.filter(username=username).exists():
                err_value = f'логином - {username}'
            return Response(
                f'Пользователь с {err_value}, уже существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='YaMDb registration',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenViewSet(
        mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Вьюсет для получения JWT токена.
    """
    queryset = User.objects.all()
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """
        Метод реализует создание JWT-токена.
        """
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListCreatDestroyViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet,):
    pass


class CategoryViewSet(ListCreatDestroyViewSet):
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


class GenreViewSet(ListCreatDestroyViewSet):
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
        if self.request.method in ('PATCH', 'POST'):
            return TitleSerializer
        return TitleReadOnlySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с объектами Review.

    Параметры:
        - Включает CRUD-операции, связь с объектами Tile.
        - Необходимо указать title_id в URL для работы с отзывами:
        /titles/{title_id}/reviews/.
    """
    queryset = Review.objects.order_by('id')
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от метода запроса.
        """
        if self.request.method == 'GET':
            return (permissions.AllowAny(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ['PATCH', 'DELETE']:
            return (IsModeratorOrAdmin(),)
        else:
            return super().get_permissions()

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
    Вьюсет для работы с объектами Comment.

    Параметры:
        - Включает CRUD-операции, связь с объектами Review.
        - Необходимо указать title_id и review_id в URL для работы с
        комментариями: /titles/{title_id}/reviews/{review_id}/comments/.
    """
    queryset = Comment.objects.order_by('id')
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """
        Определяет права доступа в зависимости от метода запроса.
        """
        if self.request.method == 'GET':
            return (permissions.AllowAny(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
        elif self.request.method in ['PATCH', 'DELETE']:
            return (IsModeratorOrAdmin(),)
        else:
            return super().get_permissions()

    def perform_create(self, serializer):
        """
        Устанавливает автора при создании комментария.
        """
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)

    lookup_field = 'pk'
    lookup_url_kwarg = 'comment_id'
