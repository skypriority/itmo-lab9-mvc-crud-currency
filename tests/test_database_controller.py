"""Интеграционные тесты для :mod:`controllers.databasecontroller`.

В отличие от тестов контроллеров бизнес-логики (см.
``test_currency_controller.py`` и ``test_user_controller.py``),
здесь используется настоящая база SQLite в памяти — проверяется, что
CRUD-операции и связь через внешние ключи действительно работают
на уровне SQL.
"""

import unittest

from controllers.databasecontroller import (
    CurrencyRatesCRUD,
    DatabaseController,
    UserCRUD,
)


class TestDatabaseControllerIntegration(unittest.TestCase):
    """Проверяет CRUD и связи таблиц на реальной базе ``:memory:``."""

    def setUp(self) -> None:
        """Создаёт свежую базу данных в памяти перед каждым тестом."""
        self.db = DatabaseController()
        self.currency_crud = CurrencyRatesCRUD(self.db)
        self.user_crud = UserCRUD(self.db)

    def tearDown(self) -> None:
        """Закрывает соединение с базой данных после теста."""
        self.db.close()

    def test_currency_create_and_read(self) -> None:
        """Созданная валюта должна быть доступна через _read()."""
        self.currency_crud._create(
            [{"num_code": "840", "char_code": "USD", "name": "Доллар США",
              "value": 90.0, "nominal": 1}]
        )

        result = self.currency_crud._read()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["char_code"], "USD")
        self.assertEqual(result[0]["value"], 90.0)

    def test_currency_read_by_char_code_is_parameterized(self) -> None:
        """_read(char_code=...) должен вернуть только нужную валюту."""
        self.currency_crud._create(
            [
                {"num_code": "840", "char_code": "USD", "name": "USD",
                 "value": 90.0, "nominal": 1},
                {"num_code": "978", "char_code": "EUR", "name": "EUR",
                 "value": 91.0, "nominal": 1},
            ]
        )

        result = self.currency_crud._read(char_code="EUR")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["char_code"], "EUR")

    def test_currency_update(self) -> None:
        """_update() должен изменить курс валюты по её коду."""
        self.currency_crud._create(
            [{"num_code": "840", "char_code": "USD", "name": "USD",
              "value": 90.0, "nominal": 1}]
        )

        self.currency_crud._update({"USD": 101.1})

        result = self.currency_crud._read(char_code="USD")
        self.assertEqual(result[0]["value"], 101.1)

    def test_currency_delete(self) -> None:
        """_delete() должен удалить валюту по id."""
        self.currency_crud._create(
            [{"num_code": "840", "char_code": "USD", "name": "USD",
              "value": 90.0, "nominal": 1}]
        )
        currency_id = self.currency_crud._read()[0]["id"]

        self.currency_crud._delete(currency_id)

        self.assertEqual(self.currency_crud._read(), [])

    def test_user_currency_subscription_via_foreign_keys(self) -> None:
        """Подписка пользователя на валюту должна работать через JOIN."""
        self.currency_crud._create(
            [{"num_code": "840", "char_code": "USD", "name": "USD",
              "value": 90.0, "nominal": 1}]
        )
        currency_id = self.currency_crud._read()[0]["id"]
        user_id = self.user_crud._create("Николай")

        self.user_crud.subscribe(user_id, currency_id)
        subscribed = self.user_crud.get_subscribed_currencies(user_id)

        self.assertEqual(len(subscribed), 1)
        self.assertEqual(subscribed[0]["char_code"], "USD")

    def test_sql_injection_attempt_is_neutralized(self) -> None:
        """Попытка SQL-инъекции через char_code не должна ломать запрос.

        Так как запрос параметризован (``?``), значение всегда
        трактуется как обычная строка, а не как часть SQL.
        """
        self.currency_crud._create(
            [{"num_code": "840", "char_code": "USD", "name": "USD",
              "value": 90.0, "nominal": 1}]
        )

        malicious = "USD' OR '1'='1"
        result = self.currency_crud._read(char_code=malicious)

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
