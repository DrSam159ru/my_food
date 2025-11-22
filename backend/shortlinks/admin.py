from django.contrib import admin

from .models import ShortLink


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Конфигурация отображения коротких ссылок в админ-панели."""

    list_display = ('id', 'recipe', 'code')
    search_fields = ('code', 'recipe__name', 'recipe__author__username')
    list_select_related = ('recipe',)
