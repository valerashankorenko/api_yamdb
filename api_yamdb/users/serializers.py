from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

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


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели - User.
    Для регистрации новых пользователей.
    """
    """
    username = serializers.CharField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        )
    )
    email = serializers.EmailField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        )
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не допустимо.'
            )
        return value
    """
    class Meta:
        fields = ('username', 'email')
        model = User
