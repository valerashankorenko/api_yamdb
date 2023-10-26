from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        read_only_fields = ('name', 'slug')
        lookup_field = 'slug'
        lookup_url_kwarg = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        read_only_fields = ('name', 'slug')
        lookup_field = 'slug'
        lookup_url_kwarg = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    reting = serializers.IntegerField(
        source='', default=1, read_only=True
    )
    genre = SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'reting', 'description', 'genre', 'category')
        lookup_field = 'slug'
        lookup_url_kwarg = 'slug'


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
