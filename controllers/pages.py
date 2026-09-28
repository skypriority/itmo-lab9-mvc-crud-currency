"""Контроллер рендеринга страниц (View-слой приложения MVC).

Модуль отделяет логику подготовки данных для шаблонов Jinja2 от
логики маршрутизации в :mod:`myapp`. Каждый публичный метод класса
:class:`PagesController` соответствует одному маршруту приложения и
возвращает готовую HTML-строку.
"""

from jinja2 import Environment

from controllers.currencycontroller import CurrencyController
from controllers.usercontroller import UserController
from models.author import Author

#: Пункты главного меню, общие для всех страниц приложения.
NAVIGATION = [
    {"caption": "Главная", "href": "/"},
    {"caption": "Об авторе", "href": "/author"},
    {"caption": "Пользователи", "href": "/users"},
    {"caption": "Валюты", "href": "/currencies"},
]


class PagesController:
    """Готовит контекст и рендерит HTML-страницы через Jinja2.

    Attributes:
        env: Окружение Jinja2, созданное один раз в главном модуле
            приложения и переиспользуемое всеми страницами.
        author: Данные об авторе работы, отображаемые на главной и на
            странице «Об авторе».
        currency_controller: Контроллер бизнес-логики валют.
        user_controller: Контроллер бизнес-логики пользователей.
    """

    def __init__(
        self,
        env: Environment,
        author: Author,
        currency_controller: CurrencyController,
        user_controller: UserController,
    ) -> None:
        """Инициализирует контроллер страниц.

        Args:
            env: Переиспользуемое окружение Jinja2.
            author: Объект автора работы.
            currency_controller: Контроллер бизнес-логики валют.
            user_controller: Контроллер бизнес-логики пользователей.
        """
        self.env = env
        self.author = author
        self.currency_controller = currency_controller
        self.user_controller = user_controller

    def render_index(self, message: str = "") -> str:
        """Рендерит главную страницу со списком валют.

        Args:
            message: Необязательное сообщение о результате последней
                операции (например, об обновлении курса).

        Returns:
            Готовая HTML-страница.
        """
        template = self.env.get_template("index.html")
        return template.render(
            myapp="CurrenciesListApp",
            navigation=NAVIGATION,
            author_name=self.author.name,
            author_group=self.author.group,
            currencies=self.currency_controller.list_currencies(),
            result=message,
        )

    def render_author(self) -> str:
        """Рендерит страницу с информацией об авторе.

        Returns:
            Готовая HTML-страница.
        """
        template = self.env.get_template("author.html")
        return template.render(
            myapp="CurrenciesListApp",
            navigation=NAVIGATION,
            author_name=self.author.name,
            author_group=self.author.group,
        )

    def render_users(self) -> str:
        """Рендерит страницу со списком пользователей.

        Returns:
            Готовая HTML-страница.
        """
        template = self.env.get_template("users.html")
        return template.render(
            myapp="CurrenciesListApp",
            navigation=NAVIGATION,
            users=self.user_controller.list_users(),
        )

    def render_user(self, user_id: int) -> str:
        """Рендерит страницу одного пользователя с его подписками.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Готовая HTML-страница.
        """
        template = self.env.get_template("user.html")
        user = self.user_controller.get_user(user_id)
        currencies = (
            self.user_controller.get_user_currencies(user_id) if user else []
        )
        return template.render(
            myapp="CurrenciesListApp",
            navigation=NAVIGATION,
            user=user,
            currencies=currencies,
        )

    def render_currencies(self, message: str = "") -> str:
        """Рендерит страницу со списком всех валют.

        Args:
            message: Необязательное сообщение о результате последней
                операции.

        Returns:
            Готовая HTML-страница.
        """
        template = self.env.get_template("currencies.html")
        return template.render(
            myapp="CurrenciesListApp",
            navigation=NAVIGATION,
            currencies=self.currency_controller.list_currencies(),
            result=message,
        )
