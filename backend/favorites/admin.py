from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройки отображения модели Favorite в административной панели."""

    list_display = ('id', 'user', 'recipe', 'added_at')
    search_fields = ('user__username', 'user__email', 'recipe__name')
    list_select_related = ('user', 'recipe')
    ordering = ('-added_at',)
