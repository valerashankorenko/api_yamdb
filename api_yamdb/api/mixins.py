from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import User
from .serializers import (TokenSerializer,
                          UserRegisterSerializer,
                          UserSerializer)
from .utils import send_confirmation_code
# реализовано для избежания дублирования кода


class UserRegisterMixin(CreateModelMixin):
    """
    Миксин для регистрации новых пользователей.
    """

    def create(self, request):
        """
        Метод реализует:
        - создание нового пользователя,
        - отправку на его почту - кода подтверждения.
        """
        serializer = UserRegisterSerializer(data=request.data)
        if User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).exists():
            # Отправка повторного кода подтверждения,
            # зарегистрированному ранее пользователю
            send_confirmation_code(request)
            return Response(request.data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code(request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenMixin(CreateModelMixin):
    """
    Миксин для получения JWT токена.
    """

    def create(self, request):
        """
        Метод реализует создание JWT-токена по коду подтверждения.
        """
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        if not User.objects.filter(username=username).exists():
            return Response(
                {'username': ['Такого пользователя не существует.']},
                status=status.HTTP_404_NOT_FOUND
            )
        user = User.objects.get(username=username)
        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(
            {'confirmation_code': ['Неверный код подтверждения']},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserModelMixin(CreateModelMixin, ListModelMixin):
    """
    Миксин для работы с моделью - User.
    """

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


class TitleMixin(ListModelMixin,
                 CreateModelMixin,
                 DestroyModelMixin):
    """
    Миксин для работы с моделью - Title.
    """
    pass
