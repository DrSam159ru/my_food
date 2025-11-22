from urllib.parse import urljoin

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

from .models import ShortLink


def resolve_shortlink(request, code: str):
    """
    Находит короткую ссылку по коду и перенаправляет на страницу рецепта.
    """
    sl = get_object_or_404(ShortLink, code=code)
    target = urljoin(settings.FRONTEND_BASE_URL, f'recipes/{sl.recipe_id}')
    return redirect(target)
