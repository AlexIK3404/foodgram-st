import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from api.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_path',
            type=str,
            help='Путь к JSON-файлу со списком ингредиентов'
        )

    def handle(self, *args, **options):
        path = Path(options['json_path'])
        if not path.exists():
            raise CommandError(f'Файл не найден: {path}')

        self.stdout.write(f'Читаю файл {path}...')
        data = json.loads(path.read_text(encoding='utf-8'))

        created = 0
        skipped = 0
        for item in data:
            name = item.get('name')
            unit = item.get('measurement_unit')
            if not name or not unit:
                self.stderr.write(f'Пропускаю некорректную запись: {item}')
                skipped += 1
                continue

            obj, was_created = Ingredient.objects.get_or_create(
                name=name,
                defaults={'unit': unit}
            )
            if was_created:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создан ингредиент: {obj}')
                )
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Создано: {created}, пропущено \
            (уже было или ошибки): {skipped}.'
        ))
