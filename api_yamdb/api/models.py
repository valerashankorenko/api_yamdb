from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models


def validate_year(value):
    if value > datetime.now().year:
        raise ValidationError('Указанный %(value)s  год больше текущего',
                              params={'value': value})


class NameSlugModel(models.Model):
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        abstract = True


class Category(NameSlugModel):
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(NameSlugModel):
    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=256)
    year = models.IntegerField('Год выхода произведения',
                               validators=[validate_year])
    reting = models.IntegerField('Рейтинг')
    description = models.TextField('Описание')
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

    class Meta:
        verbose_name = 'Произведение-Жанр'
        verbose_name_plural = 'Произведения-Жанры'

    def __str__(self):
        return f'{self.title} - {self.genre}'
