from django.apps import AppConfig


class ShortlinksConfig(AppConfig):
    """Конфигурация приложения Shortlinks."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shortlinks'
    verbose_name = 'Короткие ссылки'

    def ready(self):
        """Импортирует сигналы при загрузке приложения."""
        from . import signals  # noqa: F401
