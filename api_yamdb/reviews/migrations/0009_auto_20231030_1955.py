# Generated by Django 3.2 on 2023-10-30 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0008_alter_genre_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(verbose_name='Слаг'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=models.SlugField(verbose_name='Слаг'),
        ),
    ]
