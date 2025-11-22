from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Настройки конфигурации для приложения API."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
