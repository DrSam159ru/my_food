from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

from recipes.models import Recipe


class Favorite(models.Model):
    """
    Связь пользователя и рецепта, добавленного в избранное.
    Хранит дату добавления и обеспечивает уникальность пары.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт',
    )
    added_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        """Метаданные модели избранного: уникальность, индексы и сортировка."""

        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite',
            )
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['recipe']),
            models.Index(fields=['user', 'added_at']),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['-added_at']

    def __str__(self):
        """Возвращает строковое представление избранного рецепта."""
        return f'{self.user} → {self.recipe}'
