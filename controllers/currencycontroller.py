"""Контроллер бизнес-логики для сущности «Валюта».

Отделяет бизнес-логику приложения от прямого доступа к базе данных:
контроллер принимает объект :class:`CurrencyRatesCRUD` и делегирует ему
операции чтения/записи, не работая с SQL напрямую.
"""

from typing import Any

from controllers.databasecontroller import CurrencyRatesCRUD


class CurrencyController:
    """Контроллер бизнес-логики для работы со списком валют.

    Attributes:
        db: CRUD-контроллер, инкапсулирующий доступ к таблице
            ``currency`` в базе данных.
    """

    def __init__(self, db_controller: CurrencyRatesCRUD) -> None:
        """Инициализирует контроллер.

        Args:
            db_controller: Готовый CRUD-контроллер валют.
        """
        self.db = db_controller

    def list_currencies(self) -> list[dict[str, Any]]:
        """Возвращает список всех валют.

        Returns:
            Список словарей с данными валют.
        """
        return self.db._read()

    def get_currency(self, char_code: str) -> list[dict[str, Any]]:
        """Возвращает валюту по буквенному коду.

        Args:
            char_code: Буквенный код валюты (например, "USD").

        Returns:
            Список словарей (обычно из одного элемента) с данными
            найденной валюты.
        """
        return self.db._read(char_code=char_code)

    def add_currency(
        self,
        num_code: str,
        char_code: str,
        name: str,
        value: float,
        nominal: int,
    ) -> None:
        """Добавляет новую валюту в базу данных.

        Args:
            num_code: Цифровой код валюты.
            char_code: Буквенный код валюты.
            name: Наименование валюты.
            value: Курс валюты.
            nominal: Номинал валюты.
        """
        self.db._create(
            [
                {
                    "num_code": num_code,
                    "char_code": char_code,
                    "name": name,
                    "value": value,
                    "nominal": nominal,
                }
            ]
        )

    def update_currency(self, char_code: str, value: float) -> None:
        """Обновляет курс валюты.

        Args:
            char_code: Буквенный код валюты.
            value: Новое значение курса.
        """
        self.db._update({char_code: value})

    def delete_currency(self, currency_id: int) -> None:
        """Удаляет валюту по идентификатору.

        Args:
            currency_id: Идентификатор записи в таблице ``currency``.
        """
        self.db._delete(currency_id)
