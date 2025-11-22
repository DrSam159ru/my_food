from django.db.models.signals import post_save
from django.dispatch import receiver

from recipes.models import Recipe

from .models import ShortLink


@receiver(post_save, sender=Recipe)
def create_shortlink_for_recipe(
    sender,
    instance: Recipe,
    created: bool,
    **kwargs
):
    """
    Создаёт короткую ссылку для нового рецепта, если она ещё не существует.
    """
    if created and not hasattr(instance, 'shortlink'):
        ShortLink.objects.create(recipe=instance)
