from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
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


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериалайзел для POST, RATCH и DEL запросов.
    """
    genre = SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        genre = Genre.objects.filter(slug__in=data['genre'])
        category = Category.objects.get(slug=data['category'])
        data['genre'] = GenreSerializer(instance=genre, many=True).data
        data['category'] = CategorySerializer(instance=category).data
        return data


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """
    Сериалайзел для GET запросов.
    """
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


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
