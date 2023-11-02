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
    name = serializers.CharField(required=True, max_length=256)

    genre = SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Имя должно быть меньше или равно 256 символам.')
        return value

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """
    Сериалайзел для GET запросов.
    """
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True,)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


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
        existing_review = Review.objects.filter(
            title=validated_data['title'], author=self.context['request'].user
        ).exists()
        if existing_review:
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
