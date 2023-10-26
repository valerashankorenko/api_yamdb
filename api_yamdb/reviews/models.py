from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

LENGTH_TITLE = 20


class Title(models.Model):
    ...
# Добавить поле в модель
# rating = models.OneToOneField(
#    Rating, on_delete=models.CASCADE, null=True, blank=True)


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
