from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

from recipes.models import Recipe


class ShoppingList(models.Model):
    """Элемент списка покупок, содержащий рецепт пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепт',
    )
    added_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        """Метаданные модели ShoppingList."""

        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_cartitem',
            )
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['recipe']),
            models.Index(fields=['user', 'added_at']),
        ]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Список покупок'
        ordering = ['-added_at']

    def __str__(self):
        """Возвращает строковое представление записи."""
        return f'{self.user} → {self.recipe}'
