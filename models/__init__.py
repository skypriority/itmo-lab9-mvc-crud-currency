"""Пакет моделей бизнес-логики приложения.

Содержит классы-сущности предметной области: :class:`Author`,
:class:`Currency` и :class:`User`. Модели инкапсулируют данные через
приватные атрибуты и предоставляют доступ к ним через свойства
(``property``) с валидацией в сеттерах.
"""

from .author import Author
from .currency import Currency
from .user import User

__all__ = ["Author", "Currency", "User"]
