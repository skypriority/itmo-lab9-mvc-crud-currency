"""Модель пользователя.

Модуль содержит класс :class:`User`, описывающий пользователя
приложения, который может быть подписан на список валют.
"""

from typing import Optional


class User:
    """Представляет пользователя приложения.

    Attributes:
        name: Имя пользователя.
    """

    def __init__(self, name: str, user_id: Optional[int] = None) -> None:
        """Инициализирует пользователя.

        Args:
            name: Имя пользователя (не менее 2 символов).
            user_id: Идентификатор записи в базе данных (если
                пользователь уже сохранён).

        Raises:
            ValueError: Если имя не проходит валидацию.
        """
        self.name = name
        self.__id = user_id

    @property
    def id(self) -> Optional[int]:
        """Optional[int]: Идентификатор записи в базе данных."""
        return self.__id

    @property
    def name(self) -> str:
        """str: Имя пользователя."""
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        if isinstance(name, str) and len(name) >= 2:
            self.__name = name
        else:
            raise ValueError("Ошибка при задании имени пользователя")

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта для отладки."""
        return f"User(id={self.__id!r}, name={self.__name!r})"
