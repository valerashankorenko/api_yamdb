from rest_framework import serializers
# from rest_framework.validators import UniqueValidator

from .models import User


class TokenSerializer(serializers.ModelSerializer):
    """
    Сериализатор для токена.
    """
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели - User.
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class UserEditSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели - User.
    Для самостоятельного редактирования пользователем своего профиля.
    """
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        model = User
        read_only_fields = ('role',)


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели - User.
    Для регистрации новых пользователей.
    """
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        return value

    class Meta:
        model = User
        fields = (
            'username', 'email'
        )
