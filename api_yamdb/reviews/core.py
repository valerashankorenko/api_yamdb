from django.db import models


class NameSlugModel(models.Model):
    """
    Абстрактная модель.
    """
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        abstract = True
