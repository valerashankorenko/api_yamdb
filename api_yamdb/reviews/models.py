from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models import Avg

LENGTH_TITLE = 20


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = (
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя (логин)',
        max_length=150,
        unique=True,
        validators=([RegexValidator(regex=r'^[\w.@+-]+$')]),
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True
    )
    bio = models.TextField(
        verbose_name='О себе',
        null=True,
        blank=True
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLES,
        default=USER
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=200,
        editable=False,
        null=True,
        blank=True,
        unique=True
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


def validate_year(value):
    if value > datetime.now().year:
        raise ValidationError('Указанный %(value)s  год больше текущего',
                              params={'value': value})


class NameSlugModel(models.Model):
    name = models.CharField('Название категории', max_length=256,
                            editable=False)
    slug = models.SlugField('Слаг', max_length=50)

    class Meta:
        abstract = True


class Category(NameSlugModel):
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        unique_together = ('slug',)

    def __str__(self):
        return self.name


class Genre(NameSlugModel):

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        unique_together = ('slug',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=256)
    year = models.IntegerField('Год выхода произведения',
                               validators=[validate_year])
    rating = models.OneToOneField(
        'Rating', on_delete=models.CASCADE,
        null=True, blank=True, related_name='title_rating')
    description = models.TextField('Описание', null=True, blank=True)
    genre = models.ManyToManyField(Genre, through='TitleGenre',
                                   verbose_name='Жанр')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 related_name='titles', null=True,
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
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор отзыва')
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
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор комментария')
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
    title = models.OneToOneField(Title, on_delete=models.CASCADE,
                                 related_name='title_rating',
                                 verbose_name='Название произведения')
    score = models.IntegerField('Рейтинг произведения', null=True, blank=True)

    def update_score(self):
        reviews = self.title.reviews.all()
        if reviews.exists():
            self.score = reviews.aggregate(Avg('score'))['score__avg']
            if self.score is not None:
                self.save()

    def __str__(self):
        return f'{self.title.name} - {self.score}'
