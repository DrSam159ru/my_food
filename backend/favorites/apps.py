from django.apps import AppConfig


class FavoritesConfig(AppConfig):
    """Конфигурация приложения избранных рецептов."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'favorites'
    verbose_name = 'Избранное'
