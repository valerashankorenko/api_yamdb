# Generated by Django 3.2.15 on 2023-10-29 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20231029_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='reting',
            field=models.IntegerField(verbose_name='Рейтинг'),
        ),
    ]
