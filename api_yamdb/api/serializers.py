from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title, User


class TokenSerializer(serializers.ModelSerializer):
    """
    Сериализатор для токена.
    """
    username = serializers.CharField(
        required=True)
    confirmation_code = serializers.CharField(
        required=True)

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


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели - Category.
    """
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        lookup_url_kwarg = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели - Genre.
    """
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        lookup_url_kwarg = 'slug'


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """
    Сериализатор для GET запросов.
    """
    rating = serializers.IntegerField(
        read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для POST, PATCH и DELETE запросов.
    """
    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Создать произведение без жанра невозможно'
            )
        return value

    def to_representation(self, instance):
        return TitleReadOnlySerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review, представляет поля:
    id title, text, author, score и pub_date.
    Включает особую обработку для поля author.
    """
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'text', 'author', 'score', 'pub_date'
        )

    def create(self, validated_data):
        """
        Метод проверяет отзыв на дубликат.
        """
        if Review.objects.filter(
            title=validated_data['title'],
            author=self.context['request'].user
        ).exists():
            raise serializers.ValidationError(
                'На одно произведение пользователь'
                'может оставить только один отзыв'
            )
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment, представляет поля:
    id review, text, author и pub_date.
    Включает особую обработку для поля author.
    """
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = fields = (
            'id', 'text', 'author', 'pub_date'
        )
