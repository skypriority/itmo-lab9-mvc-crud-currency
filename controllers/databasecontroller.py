"""Контроллер для работы с базой данных SQLite.

Модуль инкапсулирует всю работу с SQLite-базой в памяти
(``sqlite3.connect(':memory:')``): создание схемы (таблицы ``user``,
``currency`` и связующей таблицы ``user_currency``), а также CRUD-операции
над валютами и пользователями. Все запросы к базе — параметризованные,
что исключает SQL-инъекции.

Схема базы данных:

* ``user`` — пользователи приложения. Первичный ключ ``id``.
* ``currency`` — курсы валют. Первичный ключ ``id``.
* ``user_currency`` — таблица связи "многие ко многим" между
  пользователями и валютами (подписки пользователя на валюты).
  Содержит внешние ключи ``user_id`` и ``currency_id``, ссылающиеся на
  таблицы ``user`` и ``currency`` соответственно.

Первичный ключ (PRIMARY KEY) однозначно идентифицирует запись в таблице
и гарантирует её уникальность. Внешний ключ (FOREIGN KEY) связывает
запись одной таблицы с записью другой, поддерживая ссылочную
целостность данных — например, не позволяет подписать пользователя на
несуществующую валюту.
"""

import sqlite3
from typing import Any, Iterable, Mapping, Optional

from models.currency import Currency
from models.user import User


class DatabaseController:
    """Базовый контроллер соединения с базой данных SQLite в памяти.

    Создаёт единое соединение и включает поддержку внешних ключей.
    От этого класса наследуются конкретные CRUD-контроллеры сущностей,
    что позволяет им работать с одной и той же базой данных.
    """

    def __init__(self, connection: Optional[sqlite3.Connection] = None) -> None:
        """Инициализирует соединение с базой данных.

        Args:
            connection: Готовое соединение SQLite. Если не передано,
                создаётся новое соединение с базой в памяти
                (``:memory:``). Передача общего соединения нужна, чтобы
                разные контроллеры (валюты, пользователи) работали с
                одной и той же базой в памяти.
        """
        self._con = connection or sqlite3.connect(":memory:")
        self._con.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    def _create_schema(self) -> None:
        """Создаёт таблицы ``user``, ``currency`` и ``user_currency``."""
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """
        )
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                num_code TEXT NOT NULL,
                char_code TEXT NOT NULL,
                name TEXT NOT NULL,
                value FLOAT,
                nominal INTEGER
            )
            """
        )
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS user_currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                currency_id INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(currency_id) REFERENCES currency(id)
            )
            """
        )
        self._con.commit()

    @property
    def connection(self) -> sqlite3.Connection:
        """sqlite3.Connection: Общее соединение с базой данных."""
        return self._con

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        self._con.close()


class CurrencyRatesCRUD:
    """CRUD-операции над таблицей ``currency``.

    Все запросы параметризованы (используют плейсхолдеры ``?`` или
    именованные параметры ``:name``), что защищает от SQL-инъекций.
    """

    def __init__(self, db: DatabaseController) -> None:
        """Инициализирует контроллер валют.

        Args:
            db: Контроллер соединения с базой данных, схема которой
                уже создана.
        """
        self.__con = db.connection

    def _create(self, currencies: Iterable[Mapping[str, Any]]) -> None:
        """Добавляет одну или несколько валют в базу данных.

        Args:
            currencies: Итерируемый набор словарей с ключами
                ``num_code``, ``char_code``, ``name``, ``value``,
                ``nominal`` — по одному словарю на добавляемую валюту.

        Пример:
            >>> data = [{"num_code": "840", "char_code": "USD",
            ...          "name": "Доллар США", "value": 90.0,
            ...          "nominal": 1}]
            >>> crud._create(data)
        """
        sql = (
            "INSERT INTO currency(num_code, char_code, name, value, nominal) "
            "VALUES(:num_code, :char_code, :name, :value, :nominal)"
        )
        self.__con.executemany(sql, list(currencies))
        self.__con.commit()

    def _read(
        self, char_code: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Возвращает список валют из базы данных.

        Args:
            char_code: Если указан, возвращает только валюту с данным
                буквенным кодом (параметризованный запрос). Если не
                указан — возвращает все валюты.

        Returns:
            Список словарей с полями ``id``, ``num_code``, ``char_code``,
            ``name``, ``value``, ``nominal``.
        """
        if char_code is not None:
            sql = "SELECT * FROM currency WHERE char_code = ?"
            cursor = self.__con.execute(sql, (char_code,))
        else:
            cursor = self.__con.execute("SELECT * FROM currency")

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def _update(self, currency: Mapping[str, float]) -> None:
        """Обновляет курс валюты по буквенному коду.

        Args:
            currency: Словарь вида ``{"USD": 101.1}`` — буквенный код
                валюты в качестве ключа и новое значение курса.

        Пример:
            >>> crud._update({"USD": 101.1})
        """
        char_code, value = next(iter(currency.items()))
        sql = "UPDATE currency SET value = ? WHERE char_code = ?"
        self.__con.execute(sql, (value, char_code))
        self.__con.commit()

    def _delete(self, currency_id: int) -> None:
        """Удаляет валюту по идентификатору.

        Args:
            currency_id: Идентификатор записи в таблице ``currency``.
        """
        sql = "DELETE FROM currency WHERE id = ?"
        self.__con.execute(sql, (int(currency_id),))
        self.__con.commit()


class UserCRUD:
    """CRUD-операции над таблицей ``user`` и подписками на валюты."""

    def __init__(self, db: DatabaseController) -> None:
        """Инициализирует контроллер пользователей.

        Args:
            db: Контроллер соединения с базой данных, схема которой
                уже создана.
        """
        self.__con = db.connection

    def _create(self, name: str) -> int:
        """Добавляет пользователя в базу данных.

        Args:
            name: Имя пользователя.

        Returns:
            Идентификатор созданной записи.
        """
        sql = "INSERT INTO user(name) VALUES(?)"
        cursor = self.__con.execute(sql, (name,))
        self.__con.commit()
        return int(cursor.lastrowid)

    def _read(self, user_id: Optional[int] = None) -> list[dict[str, Any]]:
        """Возвращает список пользователей.

        Args:
            user_id: Если указан, возвращает только пользователя с
                данным идентификатором.

        Returns:
            Список словарей с полями ``id``, ``name``.
        """
        if user_id is not None:
            sql = "SELECT * FROM user WHERE id = ?"
            cursor = self.__con.execute(sql, (int(user_id),))
        else:
            cursor = self.__con.execute("SELECT * FROM user")

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def _update(self, user_id: int, name: str) -> None:
        """Обновляет имя пользователя.

        Args:
            user_id: Идентификатор пользователя.
            name: Новое имя.
        """
        sql = "UPDATE user SET name = ? WHERE id = ?"
        self.__con.execute(sql, (name, int(user_id)))
        self.__con.commit()

    def _delete(self, user_id: int) -> None:
        """Удаляет пользователя по идентификатору.

        Args:
            user_id: Идентификатор записи в таблице ``user``.
        """
        sql = "DELETE FROM user WHERE id = ?"
        self.__con.execute(sql, (int(user_id),))
        self.__con.commit()

    def subscribe(self, user_id: int, currency_id: int) -> None:
        """Подписывает пользователя на валюту.

        Создаёт запись в связующей таблице ``user_currency``.

        Args:
            user_id: Идентификатор пользователя (внешний ключ).
            currency_id: Идентификатор валюты (внешний ключ).
        """
        sql = "INSERT INTO user_currency(user_id, currency_id) VALUES(?, ?)"
        self.__con.execute(sql, (int(user_id), int(currency_id)))
        self.__con.commit()

    def get_subscribed_currencies(self, user_id: int) -> list[dict[str, Any]]:
        """Возвращает валюты, на которые подписан пользователь.

        Использует ``JOIN`` таблиц ``user_currency`` и ``currency`` по
        внешнему ключу ``currency_id``.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Список словарей с данными валют (``id``, ``num_code``,
            ``char_code``, ``name``, ``value``, ``nominal``).
        """
        sql = (
            "SELECT c.id, c.num_code, c.char_code, c.name, c.value, "
            "c.nominal FROM currency c "
            "JOIN user_currency uc ON uc.currency_id = c.id "
            "WHERE uc.user_id = ?"
        )
        cursor = self.__con.execute(sql, (int(user_id),))
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def row_to_currency(row: Mapping[str, Any]) -> Currency:
    """Преобразует строку из базы данных в объект :class:`Currency`.

    Args:
        row: Словарь с ключами ``num_code``, ``char_code``, ``name``,
            ``value``, ``nominal`` и, опционально, ``id``.

    Returns:
        Объект :class:`Currency`, построенный из переданных данных.
    """
    return Currency(
        num_code=row["num_code"],
        char_code=row["char_code"],
        name=row["name"],
        value=row["value"],
        nominal=row["nominal"],
        currency_id=row.get("id"),
    )


def row_to_user(row: Mapping[str, Any]) -> User:
    """Преобразует строку из базы данных в объект :class:`User`.

    Args:
        row: Словарь с ключами ``name`` и, опционально, ``id``.

    Returns:
        Объект :class:`User`, построенный из переданных данных.
    """
    return User(name=row["name"], user_id=row.get("id"))
