from rest_framework import serializers

from reviews.models import Comment, Review


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
