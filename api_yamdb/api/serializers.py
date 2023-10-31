import re

from django.utils import timezone
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


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


class CategorySerializer(serializers.Serializer):
    """
    Сериализатор для модели Category.
    """
    name = serializers.CharField(required=True, max_length=256)
    slug = serializers.CharField(required=True, max_length=50)

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Имя должно быть меньше или равно 256 символам.')
        return value

    def validate_slug(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                'Слаг должен быть меньше или равен 50 символам.')
        if not re.match(r'^[-a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                'Слаг должен содержать только буквы, цифры,'
                'дефисы и символы подчеркивания.')
        return value

    def create(self, validated_data):
        category = Category.objects.create(
            name=validated_data['name'],
            slug=validated_data['slug']
        )
        return category

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        lookup_url_kwarg = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.
    """
    name = serializers.CharField(required=True, max_length=256)
    slug = serializers.CharField(required=True, max_length=50)

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Имя должно быть меньше или равно 256 символам.')
        return value

    def validate_slug(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                'Слаг должен быть меньше или равен 50 символам.')
        if not re.match(r'^[-a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                'Слаг должен содержать только буквы, цифры,'
                'дефисы и символы подчеркивания.')
        return value

    def create(self, validated_data):
        genre = Genre.objects.create(
            name=validated_data['name'],
            slug=validated_data['slug']
        )
        return genre

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        lookup_url_kwarg = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.
    """

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Имя должно быть меньше или равно 256 символам.')
        return value

    def validate_year(self, value):
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выхода произведения не может быть больше текущего года.')
        return value

    def validate_category(self, value):
        try:
            Category.objects.get(name=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                'Указанная категория не существует.')
        return value

    def validate_genre(self, value):
        try:
            Genre.objects.get(name=value)
        except Genre.DoesNotExist:
            raise serializers.ValidationError('Указанный жанр не существует.')
        return value

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment, представляет поля:
    id review, text, author и pub_date.
    Включает особую обработку для поля author.
    """
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review, представляет поля:
    id title, text, author, score и pub_date.
    Включает особую обработку для поля author.
    """
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
