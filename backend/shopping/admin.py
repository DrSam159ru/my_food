from django.contrib import admin

from .models import ShoppingList


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Настройки отображения модели ShoppingList в админ-панели."""

    list_display = ('id', 'user', 'recipe', 'added_at')
    search_fields = ('user__username', 'user__email', 'recipe__name')
    list_select_related = ('user', 'recipe')
    ordering = ('-added_at',)
