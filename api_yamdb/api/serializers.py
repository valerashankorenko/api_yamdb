from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Title


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
