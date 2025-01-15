from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers.user_manager import CustomUserManager


class CustomUser(AbstractUser):

    user_id = models.BigIntegerField(
        unique=True, editable=False, verbose_name='Telegram ID'
    )
    username = models.CharField(
        max_length=150, blank=True, null=True
    )
    email = models.EmailField(
        blank=True, null=True,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=150, blank=True, null=True
    )
    last_name = models.CharField(
        max_length=150, blank=True, null=True
    )
    avatar = models.ImageField(
        upload_to='users/', blank=True,
        null=True, verbose_name='Аватар'
    )

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()  # Используем кастомный менеджер

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return (
            self.username if self.username else f'Пользователь {self.user_id}'
        )


class Tag(models.Model):

    name = models.CharField(
        max_length=32, unique=True,
        verbose_name='Тема'
    )
    slug = models.SlugField(
        max_length=32, unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Question(models.Model):

    name = models.CharField(
        max_length=150, unique=True,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    syntax = models.TextField(
        blank=True, null=True,
        verbose_name='Синтаксис'
    )
    tags = models.ManyToManyField(
        Tag, related_name='questions_python',
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.name


class UserQuestionStatistic(models.Model):

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='question_statistics'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE
    )
    attempts = models.IntegerField(default=0)
    correct_attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    rating = models.FloatField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'], name='unique_user_question'
            )
        ]

    def __str__(self):
        return (
            f'Статистика пользователя {self.user} по вопросу {self.question}'
        )
