from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User

# Кортеж связывает имя модели, имя файла CSV и ключевые поля,
# требуещие добавления суффикса _id
Model_CSV = (
    (User, 'users.csv', {}),
    (Category, 'category.csv', {}),
    (Title, 'titles.csv', {'category': 'category_id'}),
    (Genre, 'genre.csv', {}),
    (Review, 'review.csv', {'author': 'author_id'}),
    (Comment, 'comments.csv', {'author': 'author_id'}),
    (Title.genre.through, 'genre_title.csv', {}),
)


def load_data_from_csv(model_name, file_name, key_fields):
    """
    Загружает данные из файла и сохраняет их в базу данных.
    """
    model = model_name
    csv_file = f'{settings.CSV_DIR}/data/{file_name}'
    model.objects.all().delete()
    with open(csv_file, mode='r', encoding='utf-8', newline='') as csv_file:
        reader = DictReader(csv_file)
        items = []
        for row in reader:
            values = dict(**row)
            # изменяем имена ключевых полей - добавляем суффикс
            if key_fields:
                for old, new in key_fields.items():
                    values[new] = values.pop(old)
            items.append(model(**values))
        model.objects.bulk_create(items)
    print(f'Данные из {file_name} загружены.')


class Command(BaseCommand):
    help = 'Загрузка данных из CSV файлов.'

    def handle(self, *args, **options):
        for model, file_name, key_fields in Model_CSV:
            load_data_from_csv(model, file_name, key_fields)
        return 'Загрузка данных завершена.'
