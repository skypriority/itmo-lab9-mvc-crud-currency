"""Юнит-тесты для моделей :mod:`models`."""

import unittest

from models.author import Author
from models.currency import Currency
from models.user import User


class TestAuthor(unittest.TestCase):
    """Проверяет валидацию свойств :class:`Author`."""

    def test_valid_author(self) -> None:
        """Корректные имя и группа должны сохраниться без ошибок."""
        author = Author("Дмитрий Кравцов", "P3120")
        self.assertEqual(author.name, "Дмитрий Кравцов")
        self.assertEqual(author.group, "P3120")

    def test_invalid_name_raises(self) -> None:
        """Слишком короткое имя должно вызывать ValueError."""
        with self.assertRaises(ValueError):
            Author("Н", "P3120")

    def test_invalid_group_raises(self) -> None:
        """Слишком короткая группа должна вызывать ValueError."""
        with self.assertRaises(ValueError):
            Author("Николай", "P34")


class TestCurrency(unittest.TestCase):
    """Проверяет валидацию свойств :class:`Currency`."""

    def test_char_code_uppercased(self) -> None:
        """char_code должен приводиться к верхнему регистру."""
        currency = Currency("840", "usd", "Доллар США", 90.0, 1)
        self.assertEqual(currency.char_code, "USD")

    def test_invalid_char_code_length_raises(self) -> None:
        """char_code не из 3 символов должен вызывать ValueError."""
        with self.assertRaises(ValueError):
            Currency("840", "US", "Доллар США", 90.0, 1)

    def test_negative_value_raises(self) -> None:
        """Отрицательный курс должен вызывать ValueError."""
        with self.assertRaises(ValueError):
            Currency("840", "USD", "Доллар США", -1.0, 1)


class TestUser(unittest.TestCase):
    """Проверяет валидацию свойств :class:`User`."""

    def test_valid_user(self) -> None:
        """Корректное имя должно сохраниться без ошибок."""
        user = User("Мария", user_id=1)
        self.assertEqual(user.name, "Мария")
        self.assertEqual(user.id, 1)

    def test_invalid_name_raises(self) -> None:
        """Слишком короткое имя должно вызывать ValueError."""
        with self.assertRaises(ValueError):
            User("М")


if __name__ == "__main__":
    unittest.main()
