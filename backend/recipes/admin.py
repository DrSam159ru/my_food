from django.contrib import admin
from django.db.models import Count

from .models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    RecipeTag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения модели Tag в административной панели."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения модели Ingredient в админ-панели."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)


class RecipeTagInline(admin.TabularInline):
    """Инлайн для связи рецептов с тегами."""

    model = RecipeTag
    extra = 1
    autocomplete_fields = ('tag',)
    fields = ('tag',)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов рецепта."""

    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ('ingredient',)
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения рецептов в административной панели."""

    list_display = ('id', 'name', 'author', 'favorites_count')
    list_select_related = ('author',)
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (RecipeTagInline, RecipeIngredientInline)

    def get_queryset(self, request):
        """
        Добавляет аннотацию с количеством добавлений рецепта в избранное.
        """
        queryset = super().get_queryset(request)
        return queryset.annotate(
            fav_count=Count('favorited_by', distinct=True)
        )

    @admin.display(description='В избранном')
    def favorites_count(self, obj: Recipe):
        """Возвращает число пользователей, добавивших рецепт в избранное."""
        return getattr(obj, 'fav_count', 0)
