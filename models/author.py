"""Модель автора проекта.

Модуль содержит класс :class:`Author`, описывающий сведения об авторе
учебной работы: имя и учебную группу.
"""


class Author:
    """Представляет автора лабораторной работы.

    Attributes:
        name: Имя автора (не менее 2 символов).
        group: Номер учебной группы (более 5 символов).
    """

    def __init__(self, name: str, group: str) -> None:
        """Инициализирует автора.

        Args:
            name: Имя автора.
            group: Учебная группа автора.

        Raises:
            ValueError: Если имя или группа не проходят валидацию.
        """
        self.name = name
        self.group = group

    @property
    def name(self) -> str:
        """str: Имя автора."""
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        if isinstance(name, str) and len(name) >= 2:
            self.__name = name
        else:
            raise ValueError("Ошибка при задании имени автора")

    @property
    def group(self) -> str:
        """str: Учебная группа автора."""
        return self.__group

    @group.setter
    def group(self, group: str) -> None:
        if isinstance(group, str) and len(group) >= 5:
            self.__group = group
        else:
            raise ValueError("Ошибка при задании группы автора")

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта для отладки."""
        return f"Author(name={self.__name!r}, group={self.__group!r})"
