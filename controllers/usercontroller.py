"""Контроллер бизнес-логики для сущности «Пользователь».

Отвечает за операции над пользователями и за получение списка валют,
на которые подписан конкретный пользователь (связь «многие ко многим»
через таблицу ``user_currency``).
"""

from typing import Any

from controllers.databasecontroller import UserCRUD


class UserController:
    """Контроллер бизнес-логики для работы с пользователями.

    Attributes:
        db: CRUD-контроллер, инкапсулирующий доступ к таблицам
            ``user`` и ``user_currency``.
    """

    def __init__(self, db_controller: UserCRUD) -> None:
        """Инициализирует контроллер.

        Args:
            db_controller: Готовый CRUD-контроллер пользователей.
        """
        self.db = db_controller

    def list_users(self) -> list[dict[str, Any]]:
        """Возвращает список всех пользователей.

        Returns:
            Список словарей с данными пользователей.
        """
        return self.db._read()

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        """Возвращает данные одного пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Словарь с данными пользователя или ``None``, если
            пользователь не найден.
        """
        rows = self.db._read(user_id=user_id)
        return rows[0] if rows else None

    def add_user(self, name: str) -> int:
        """Создаёт нового пользователя.

        Args:
            name: Имя пользователя.

        Returns:
            Идентификатор созданного пользователя.
        """
        return self.db._create(name)

    def delete_user(self, user_id: int) -> None:
        """Удаляет пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.
        """
        self.db._delete(user_id)

    def subscribe_to_currency(self, user_id: int, currency_id: int) -> None:
        """Подписывает пользователя на валюту.

        Args:
            user_id: Идентификатор пользователя.
            currency_id: Идентификатор валюты.
        """
        self.db.subscribe(user_id, currency_id)

    def get_user_currencies(self, user_id: int) -> list[dict[str, Any]]:
        """Возвращает валюты, на которые подписан пользователь.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Список словарей с данными валют пользователя.
        """
        return self.db.get_subscribed_currencies(user_id)
