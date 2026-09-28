"""Модель валюты.

Модуль содержит класс :class:`Currency`, описывающий курс валюты
Центрального банка: цифровой и буквенный коды, наименование,
значение курса и номинал.
"""

from typing import Optional


class Currency:
    """Представляет запись о курсе валюты.

    Attributes:
        num_code: Цифровой код валюты (например, "840").
        char_code: Буквенный код валюты из 3 символов (например, "USD").
        name: Полное наименование валюты.
        value: Курс валюты к рублю. Не может быть отрицательным.
        nominal: Номинал валюты.
    """

    def __init__(
        self,
        num_code: str,
        char_code: str,
        name: str,
        value: float,
        nominal: int,
        currency_id: Optional[int] = None,
    ) -> None:
        """Инициализирует объект валюты.

        Args:
            num_code: Цифровой код валюты.
            char_code: Буквенный код валюты (будет приведён к верхнему
                регистру), должен состоять ровно из 3 символов.
            name: Наименование валюты.
            value: Курс валюты. Не может быть отрицательным.
            nominal: Номинал валюты.
            currency_id: Идентификатор записи в базе данных (если валюта
                уже сохранена).

        Raises:
            ValueError: Если ``char_code`` не из 3 символов или
                ``value`` отрицателен.
        """
        self.__num_code = num_code
        self.char_code = char_code
        self.__name = name
        self.value = value
        self.__nominal = nominal
        self.__id = currency_id

    @property
    def id(self) -> Optional[int]:
        """Optional[int]: Идентификатор записи в базе данных."""
        return self.__id

    @property
    def num_code(self) -> str:
        """str: Цифровой код валюты."""
        return self.__num_code

    @property
    def char_code(self) -> str:
        """str: Буквенный код валюты (3 символа, верхний регистр)."""
        return self.__char_code

    @char_code.setter
    def char_code(self, val: str) -> None:
        if len(val) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов")
        self.__char_code = val.upper()

    @property
    def name(self) -> str:
        """str: Наименование валюты."""
        return self.__name

    @property
    def value(self) -> float:
        """float: Курс валюты к рублю."""
        return self.__value

    @value.setter
    def value(self, val: float) -> None:
        if val < 0:
            raise ValueError("Курс валюты не может быть отрицательным")
        self.__value = float(val)

    @property
    def nominal(self) -> int:
        """int: Номинал валюты."""
        return self.__nominal

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта для отладки."""
        return (
            f"Currency(char_code={self.__char_code!r}, "
            f"value={self.__value!r})"
        )
