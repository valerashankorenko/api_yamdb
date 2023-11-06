from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator, MinValueValidator, RegexValidator)
from django.db import models

from .core import NameSlugModel

LENGTH_TITLE = 20


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    SUPERUSER = 'superuser'

    ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
        (SUPERUSER, 'Суперпользователь'),
    )

    email = models.EmailField(
        'E-mail',
        max_length=254,
        unique=True,)
    username = models.CharField(
        'Имя пользователя (логин)',
        max_length=150,
        unique=True,
        validators=(RegexValidator(regex=r'^[\w.@+-]+$'),),
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True)
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True)
    bio = models.TextField(
        'О себе',
        blank=True)
    role = models.CharField(
        'Роль',
        max_length=50,
        choices=ROLES,
        default=USER)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.role == self.SUPERUSER

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


def validate_year(value):
    """
    Метод для проверки года произведения.
    """
    if value > datetime.now().year:
        raise ValidationError('Указанный %(value)s  год больше текущего',
                              params={'value': value})


class Category(NameSlugModel):
    """
    Модель для создания категорий для произведений.
    """
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(NameSlugModel):
    """
    Модель для создания жанров для произведений.
    """
    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Модель для произведений.
    """
    name = models.CharField(
        'Название произведения',
        max_length=256)
    year = models.PositiveSmallIntegerField(
        'Год выхода произведения',
        validators=(validate_year,))
    description = models.TextField(
        'Описание',
        blank=True)
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles', null=True,
        verbose_name='Категория')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель для создания отзывов на произведения.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва')
    score = models.PositiveSmallIntegerField(
        'Оценка произведения',
        validators=(MinValueValidator(1),
                    MaxValueValidator(10)))
    pub_date = models.DateTimeField(
        'Дата публикации отзыва',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('title', 'author')

    def __str__(self):
        return self.text[:LENGTH_TITLE]


class Comment(models.Model):
    """
    Модель для создания комментариев к отзывам.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    pub_date = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:LENGTH_TITLE]
