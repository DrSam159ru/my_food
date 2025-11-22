from django.apps import AppConfig


class ShoppingConfig(AppConfig):
    """Конфигурация приложения списков покупок."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopping'
    verbose_name = 'Список покупок'
