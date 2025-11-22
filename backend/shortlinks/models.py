from urllib.parse import urljoin

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import IntegrityError, models, transaction
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

from core.const import MIN_FIELD_LENGHT
from core.utils import generate_code


CODE_VALIDATOR = RegexValidator(
    regex=r'^[A-Za-z0-9_-]+$',
    message=(
        'Код может содержать только латиницу, цифры, '
        'подчёркивание и дефис.'
    ),
)


class ShortLink(models.Model):
    """
    Короткая ссылка, привязанная к рецепту. При сохранении может
    автоматически генерировать уникальный код.
    """

    recipe = models.OneToOneField(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='shortlink',
        verbose_name='Рецепт',
    )
    code = models.CharField(
        'Код',
        max_length=MIN_FIELD_LENGHT,
        validators=[CODE_VALIDATOR],
    )
    created_at = models.DateTimeField(
        'Создано',
        auto_now_add=True,
    )

    class Meta:
        """Метаданные модели ShortLink."""

        constraints = [
            UniqueConstraint(
                Lower('code'),
                name='uniq_shortlink_code_ci',
            )
        ]
        indexes = [
            models.Index(
                Lower('code'),
                name='idx_shortlink_code_lower',
            )
        ]
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Сохраняет объект, генерируя уникальный код при его отсутствии.
        """
        if not self.code:
            length = getattr(settings, 'SHORTLINK_CODE_LENGTH', 16)
            attempts = getattr(settings, 'SHORTLINK_MAX_ATTEMPTS', 10)
            for _ in range(attempts):
                self.code = generate_code(length)
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    self.code = None
            raise RuntimeError(
                'Не удалось сгенерировать уникальный код короткой ссылки.'
            )
        return super().save(*args, **kwargs)

    def get_short_url(self) -> str:
        """
        Возвращает абсолютный URL короткой ссылки для фронтенда.
        """
        base = getattr(settings, 'FRONTEND_BASE_URL', '/')
        return urljoin(base, f's/{self.code}/')

    def __str__(self):
        """Возвращает строковое представление короткой ссылки."""
        return f'{self.code} → {self.recipe_id}'
