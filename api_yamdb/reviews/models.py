
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

LENGTH_TITLE = 20


def validate_year(value):
    if value > datetime.now().year:
        raise ValidationError('Указанный %(value)s  год больше текущего',
                              params={'value': value})


class NameSlugModel(models.Model):
    name = models.CharField('Название категории', max_length=256,
                            unique=True, blank=False, editable=False)
    slug = models.SlugField('Слаг', max_length=50, unique=True,
                            editable=False)

    class Meta:
        abstract = True


class Category(NameSlugModel):
    """
    Модель для хранения категорий.
    """

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(NameSlugModel):
    """
    Модель для хранения жанров.
    """

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    # Добавить поле в модель
    # rating = models.OneToOneField(
    #    Rating, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField('Название произведения', max_length=256,
                            editable=False)
    year = models.IntegerField('Год выхода произведения',
                               validators=[validate_year], editable=False)
    reting = models.IntegerField('Рейтинг', null=True)
    description = models.TextField('Описание', null=True, blank=True,
                                   editable=False)
    genre = models.ManyToManyField(Genre, through='TitleGenre',
                                   related_name='title', verbose_name='Жанр')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 related_name='title', null=True,
                                 verbose_name='Категория')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              verbose_name='Название произведения')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL,
                              null=True, verbose_name='Жанр')

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    """
    Модель для хранения отзывов на произведения.
    """
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    author = models.IntegerField()
    score = models.IntegerField('Рейтинг отзыва',
                                validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])
    pub_date = models.DateTimeField(
        'Дата публикации отзыва', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = (('title', 'author'),)

    def __str__(self):
        return self.text[:LENGTH_TITLE]


class Comment(models.Model):
    """
    Модель для хранения комментариев к отзывам.
    """
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария')
    author = models.IntegerField()
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:LENGTH_TITLE]


class Rating(models.Model):
    """
    Модель для хранения рейтингов произведений.

    Методы:
        - update_score: обновляет рейтинг произведения,
        рассчитывая среднее значение от всех оценок отзывов.
    """
    title = models.OneToOneField(
        'Title', on_delete=models.CASCADE,
        related_name='rating_field',
        verbose_name='Название произведения'
    )
    score = models.IntegerField('Рейтинг произведения', null=True, blank=True)

    def update_score(self):
        reviews = self.title.reviews.all()
        if reviews.exists():
            self.score = reviews.aggregate(Avg('score'))['score__avg']
            if self.score is not None:
                self.save()

    def __str__(self):
        return f'{self.title.name} - {self.score}'
