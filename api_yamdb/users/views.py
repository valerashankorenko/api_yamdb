from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from .permissions import (
    IsAdmin,
)
from .serializers import (
    TokenSerializer, UserRegisterSerializer, UserSerializer
)


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
