import csv
import os

from django.core.management.base import BaseCommand

from bot.models import Question, Tag


class Command(BaseCommand):
    help = 'Заполняет таблицу Question данными из файла questions_prod.csv'

    def handle(self, *args, **kwargs):
        # Указываем путь к файлу
        file_path = os.path.join('data', 'questions_prod.csv')

        # Проверяем существование файла
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'Файл {file_path} не найден!'))
            return

        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                name = row.get('name')
                description = row.get('description')
                syntax = row.get('syntax', '')
                tags = row.get('tags', '').split(',')

                # Проверяем обязательные поля
                if not name or not description:
                    self.stderr.write(
                        self.style.WARNING(
                            f'Пропуск строки: {
                                row
                            } (отсутствует обязательное поле)'
                        )
                    )
                    continue

                # Создаем вопрос (если он не существует)
                question, created = Question.objects.get_or_create(
                    name=name,
                    defaults={'description': description, 'syntax': syntax},
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Добавлен вопрос: {name}')
                    )
                else:
                    self.stdout.write(
                        f'Вопрос {name} уже существует. Пропуск.'
                    )

                # Добавляем теги к вопросу
                for tag_name in tags:
                    tag_name = tag_name.strip()
                    if tag_name:
                        try:
                            # Ищем тег по имени
                            tag = Tag.objects.get(name=tag_name)
                            question.tags.add(tag)
                        except Tag.DoesNotExist:
                            self.stderr.write(
                                self.style.WARNING(
                                    f'Тег "{tag_name}" не найден. Пропуск.'
                                )
                            )

        self.stdout.write(self.style.SUCCESS('Импорт завершён!'))
