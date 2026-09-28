"""Юнит-тесты для :mod:`controllers.usercontroller`.

Аналогично тестам валют, здесь бизнес-логика пользователей проверяется
изолированно от базы данных с помощью ``unittest.mock.MagicMock``.
"""

import unittest
from unittest.mock import MagicMock

from controllers.usercontroller import UserController


class TestUserController(unittest.TestCase):
    """Проверяет поведение :class:`UserController` на моках БД."""

    def test_list_users(self) -> None:
        """list_users() должен вернуть данные из db._read()."""
        mock_db = MagicMock()
        mock_db._read.return_value = [{"id": 1, "name": "Николай"}]
        controller = UserController(mock_db)

        result = controller.list_users()

        self.assertEqual(result[0]["name"], "Николай")
        mock_db._read.assert_called_once_with()

    def test_get_user_found(self) -> None:
        """get_user() должен вернуть первый элемент списка, если найден."""
        mock_db = MagicMock()
        mock_db._read.return_value = [{"id": 3, "name": "Мария"}]
        controller = UserController(mock_db)

        result = controller.get_user(3)

        mock_db._read.assert_called_once_with(user_id=3)
        self.assertEqual(result["name"], "Мария")

    def test_get_user_not_found(self) -> None:
        """get_user() должен вернуть None, если пользователь не найден."""
        mock_db = MagicMock()
        mock_db._read.return_value = []
        controller = UserController(mock_db)

        result = controller.get_user(999)

        self.assertIsNone(result)

    def test_add_user(self) -> None:
        """add_user() должен вызвать db._create() и вернуть id."""
        mock_db = MagicMock()
        mock_db._create.return_value = 42
        controller = UserController(mock_db)

        result = controller.add_user("Иван")

        mock_db._create.assert_called_once_with("Иван")
        self.assertEqual(result, 42)

    def test_delete_user(self) -> None:
        """delete_user() должен вызвать db._delete() с id."""
        mock_db = MagicMock()
        controller = UserController(mock_db)

        controller.delete_user(7)

        mock_db._delete.assert_called_once_with(7)

    def test_subscribe_to_currency(self) -> None:
        """subscribe_to_currency() должен вызвать db.subscribe()."""
        mock_db = MagicMock()
        controller = UserController(mock_db)

        controller.subscribe_to_currency(1, 2)

        mock_db.subscribe.assert_called_once_with(1, 2)

    def test_get_user_currencies(self) -> None:
        """get_user_currencies() должен вернуть данные от db."""
        mock_db = MagicMock()
        mock_db.get_subscribed_currencies.return_value = [
            {"id": 1, "char_code": "USD"}
        ]
        controller = UserController(mock_db)

        result = controller.get_user_currencies(1)

        mock_db.get_subscribed_currencies.assert_called_once_with(1)
        self.assertEqual(result[0]["char_code"], "USD")


if __name__ == "__main__":
    unittest.main()
