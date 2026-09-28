"""Юнит-тесты для :mod:`controllers.currencycontroller`.

Тесты используют ``unittest.mock.MagicMock`` для изоляции контроллера
бизнес-логики от реального доступа к базе данных: проверяется, что
:class:`CurrencyController` корректно вызывает методы CRUD-контроллера
и возвращает ожидаемые данные.
"""

import unittest
from unittest.mock import MagicMock, call

from controllers.currencycontroller import CurrencyController


class TestCurrencyController(unittest.TestCase):
    """Проверяет поведение :class:`CurrencyController` на моках БД."""

    def test_list_currencies(self) -> None:
        """list_currencies() должен вернуть данные из db._read()."""
        mock_db = MagicMock()
        mock_db._read.return_value = [
            {"id": 1, "char_code": "USD", "value": 90}
        ]
        controller = CurrencyController(mock_db)

        result = controller.list_currencies()

        self.assertEqual(result[0]["char_code"], "USD")
        mock_db._read.assert_called_once_with()

    def test_get_currency_passes_char_code(self) -> None:
        """get_currency() должен передавать char_code в db._read()."""
        mock_db = MagicMock()
        mock_db._read.return_value = [{"id": 1, "char_code": "EUR"}]
        controller = CurrencyController(mock_db)

        result = controller.get_currency("EUR")

        mock_db._read.assert_called_once_with(char_code="EUR")
        self.assertEqual(result[0]["char_code"], "EUR")

    def test_add_currency_builds_correct_payload(self) -> None:
        """add_currency() должен вызвать db._create() с одним словарём."""
        mock_db = MagicMock()
        controller = CurrencyController(mock_db)

        controller.add_currency("840", "usd", "Доллар США", 90.0, 1)

        mock_db._create.assert_called_once_with(
            [
                {
                    "num_code": "840",
                    "char_code": "usd",
                    "name": "Доллар США",
                    "value": 90.0,
                    "nominal": 1,
                }
            ]
        )

    def test_update_currency(self) -> None:
        """update_currency() должен вызвать db._update() с dict."""
        mock_db = MagicMock()
        controller = CurrencyController(mock_db)

        controller.update_currency("USD", 101.1)

        mock_db._update.assert_called_once_with({"USD": 101.1})

    def test_delete_currency(self) -> None:
        """delete_currency() должен вызвать db._delete() с id."""
        mock_db = MagicMock()
        controller = CurrencyController(mock_db)

        controller.delete_currency(5)

        mock_db._delete.assert_called_once_with(5)

    def test_multiple_calls_recorded_in_order(self) -> None:
        """Мок должен фиксировать порядок нескольких вызовов подряд."""
        mock_db = MagicMock()
        controller = CurrencyController(mock_db)

        controller.update_currency("USD", 91.0)
        controller.delete_currency(2)

        mock_db.assert_has_calls(
            [call._update({"USD": 91.0}), call._delete(2)]
        )


if __name__ == "__main__":
    unittest.main()
