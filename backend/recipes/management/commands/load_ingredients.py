import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда для загрузки ингредиентов из JSON/CSV в модель Ingredient.

    Поддерживаются файлы с полями ``name`` и ``measurement_unit``.
    """

    help = (
        'Импорт ингредиентов из JSON/CSV '
        '(колонки name, measurement_unit). '
        'Пример пути: data/ingredients.json'
    )

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки для указания пути к файлу.
        """
        parser.add_argument(
            '--path',
            default='data/ingredients.json',
            help=(
                'Путь к JSON/CSV (от корня репозитория или абсолютный путь).'
            ),
        )

    def _load_rows(self, path: Path):
        """
        Загружает строки из JSON или CSV файла и возвращает пары значений.

        Аргументы:
            path: путь к файлу с ингредиентами.

        Yields:
            Кортежи вида (name, measurement_unit) для каждого ингредиента.
        """
        ext = path.suffix.lower()
        if ext == '.json':
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    name = (item.get('name') or '').strip()
                    unit = (item.get('measurement_unit') or '').strip()
                    yield name, unit
        elif ext == '.csv':
            with path.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = (row.get('name') or '').strip()
                    unit = (row.get('measurement_unit') or '').strip()
                    yield name, unit
        else:
            raise CommandError('Поддерживаются только файлы .json и .csv.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """
        Выполняет импорт ингредиентов, если таблица ещё не заполнена.

        Если хотя бы один ингредиент уже есть в базе, импорт пропускается.
        """
        if Ingredient.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    'Ингредиенты уже есть в базе — загрузка пропущена.'
                )
            )
            return

        raw_path = opts['path']
        path = Path(raw_path)

        candidates = [
            path,
            Path('data/ingredients.json'),
            Path('data/ingredients.csv'),
        ]
        path = next((p for p in candidates if p.exists()), None)

        if not path:
            raise CommandError('Файл с ингредиентами не найден.')

        created = skipped = 0

        for name, unit in self._load_rows(path):
            if not name or not unit:
                skipped += 1
                continue

            _, was_created = Ingredient.objects.get_or_create(
                name=name,
                measurement_unit=unit,
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово: создано {created}, пропущено {skipped}. '
                f'Файл: {path}'
            )
        )
