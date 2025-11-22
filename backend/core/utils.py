import secrets
import string
from typing import Optional

from django.conf import settings

_ALPHABET = string.ascii_letters + string.digits


def generate_code(length: Optional[int] = None) -> str:
    """
    Генерирует случайный строковый код из букв и цифр.

    Параметры:
        length: длина кода. Если не указана или некорректна, используется
        значение из настроек SHORTLINK_CODE_LENGTH.

    Возвращает:
        Строку со случайными символами указанной длины.
    """
    default_length = getattr(settings, 'SHORTLINK_CODE_LENGTH', 16)

    if isinstance(length, int) and length > 0:
        n = length
    else:
        n = default_length

    return ''.join(secrets.choice(_ALPHABET) for _ in range(n))
