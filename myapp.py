"""Главный модуль приложения.

Инициализирует базу данных SQLite в памяти, создаёт контроллеры
(база данных, бизнес-логика валют/пользователей, рендеринг страниц) и
запускает HTTP-сервер на основе :class:`http.server.BaseHTTPRequestHandler`
с маршрутизацией в методе :meth:`SimpleHTTPRequestHandler.do_GET`.

Архитектура MVC:
    * Model — :mod:`models` (``Author``, ``Currency``, ``User``).
    * Controller — :mod:`controllers` (доступ к БД, бизнес-логика,
      рендеринг страниц).
    * View — HTML-шаблоны Jinja2 в каталоге ``templates``.

Запуск:
    python myapp.py

Сервер поднимается на http://localhost:8080/ со следующими маршрутами:
    * ``/``                       — главная страница со списком валют;
    * ``/author``                 — информация об авторе;
    * ``/users``                  — список пользователей;
    * ``/user?id=...``            — просмотр одного пользователя;
    * ``/currencies``             — список всех валют;
    * ``/currency/delete?id=...`` — удаление валюты;
    * ``/currency/update?char_code=USD&value=...`` — обновление курса;
    * ``/currency/show``          — вывод валют в консоль (отладка).
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from jinja2 import Environment, FileSystemLoader, select_autoescape

from controllers.currencycontroller import CurrencyController
from controllers.databasecontroller import (
    CurrencyRatesCRUD,
    DatabaseController,
    UserCRUD,
)
from controllers.pages import PagesController
from controllers.usercontroller import UserController
from models.author import Author

#: Окружение Jinja2 создаётся один раз и переиспользуется всеми
#: контроллерами рендеринга страниц приложения.
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(),
)

#: Общая база данных SQLite в памяти для всех CRUD-контроллеров.
db = DatabaseController()
currency_crud = CurrencyRatesCRUD(db)
user_crud = UserCRUD(db)

currency_controller = CurrencyController(currency_crud)
user_controller = UserController(user_crud)

#: Данные об авторе работы, отображаемые на страницах приложения.
main_author = Author("Дмитрий Кравцов", "P3120")

pages = PagesController(env, main_author, currency_controller, user_controller)


def seed_demo_data() -> None:
    """Заполняет базу данных демонстрационными данными.

    Добавляет несколько валют и пользователей с подписками, чтобы
    сразу после запуска сервера страницы не были пустыми.
    """
    demo_currencies = [
        {"num_code": "840", "char_code": "USD", "name": "Доллар США",
         "value": 90.0, "nominal": 1},
        {"num_code": "978", "char_code": "EUR", "name": "Евро",
         "value": 91.0, "nominal": 1},
        {"num_code": "826", "char_code": "GBP", "name": "Фунт стерлингов",
         "value": 100.0, "nominal": 1},
        {"num_code": "036", "char_code": "AUD", "name": "Австралийский доллар",
         "value": 52.85, "nominal": 1},
    ]
    currency_crud._create(demo_currencies)

    user1_id = user_crud._create("Николай")
    user2_id = user_crud._create("Мария")
    user3_id = user_crud._create("Ирина")

    usd_id = currency_crud._read(char_code="USD")[0]["id"]
    eur_id = currency_crud._read(char_code="EUR")[0]["id"]
    gbp_id = currency_crud._read(char_code="GBP")[0]["id"]
    user_crud.subscribe(user1_id, usd_id)
    user_crud.subscribe(user1_id, eur_id)
    user_crud.subscribe(user2_id, eur_id)
    user_crud.subscribe(user3_id, gbp_id)


seed_demo_data()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов, реализующий маршрутизацию приложения.

    Метод :meth:`do_GET` разбирает путь запроса и делегирует
    подготовку ответа соответствующим контроллерам (страницы —
    :data:`pages`, бизнес-логика — :data:`currency_controller` /
    :data:`user_controller`).
    """

    def _send_html(self, body: str, status: int = 200) -> None:
        """Отправляет клиенту HTML-ответ.

        Args:
            body: Готовая HTML-страница.
            status: HTTP-код ответа.
        """
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802 (имя метода задано http.server)
        """Обрабатывает GET-запросы согласно таблице маршрутов."""
        path = self.path.rpartition("?")[0] or self.path
        query = parse_qs(self.path.rpartition("?")[-1])

        if path == "/" or self.path == "/":
            self._send_html(pages.render_index())
            return

        if path == "/author":
            self._send_html(pages.render_author())
            return

        if path == "/users":
            self._send_html(pages.render_users())
            return

        if path == "/user":
            user_id = int(query["id"][0]) if "id" in query else 0
            self._send_html(pages.render_user(user_id))
            return

        if path == "/currencies":
            self._send_html(pages.render_currencies())
            return

        if path == "/currency/delete":
            currency_id = int(query["id"][0])
            currency_controller.delete_currency(currency_id)
            self._send_html(
                pages.render_currencies(
                    message=f"Валюта id={currency_id} удалена"
                )
            )
            return

        if path == "/currency/update":
            # Поддерживаются два формата запроса:
            #   /currency/update?char_code=USD&value=99.5 (явный, основной)
            #   /currency/update?USD=99.5 (короткий формат из задания)
            if "char_code" in query and "value" in query:
                char_code = query["char_code"][0]
                value = float(query["value"][0])
            else:
                char_code, raw_value = next(iter(query.items()))
                value = float(raw_value[0])
            currency_controller.update_currency(char_code, value)
            self._send_html(
                pages.render_currencies(
                    message=f"Курс {char_code} обновлён на {value}"
                )
            )
            return

        if path == "/currency/show":
            print(currency_controller.list_currencies())
            self._send_html("<html><body>OK, см. консоль сервера</body></html>")
            return

        self._send_html("<html><body>404 Not Found</body></html>", status=404)


def run(host: str = "localhost", port: int = 8080) -> None:
    """Запускает HTTP-сервер приложения.

    Args:
        host: Хост, на котором слушает сервер.
        port: Порт, на котором слушает сервер.
    """
    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    print(f"server is running on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
