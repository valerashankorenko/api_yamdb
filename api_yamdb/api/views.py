from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets

from reviews.models import Comment, Review, Title
from .permissions import AllowAny, IsAdmin, IsOwner
from .serializers import CommentSerializer, ReviewSerializer

# IsAdmin импортировать из приложения User


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с объектами Review.

    Параметры:
        - Включает CRUD-операции, связь с объектами Tile.
        - Необходимо указать title_id в URL для работы с отзывами:
        /titles/{title_id}/reviews/.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (AllowAny,)

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
    permission_classes = (AllowAny,)

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
