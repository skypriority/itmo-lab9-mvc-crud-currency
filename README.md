# Лабораторная работа №9. CRUD, SQLite, MVC (Currency & User)

Учебный проект на «голом» Python: HTTP-сервер (`http.server`), шаблоны
Jinja2 и база данных SQLite в памяти (`:memory:`). Реализован CRUD для
сущности `Currency`, работа с пользователями (`User`) и связь
«многие ко многим» между ними через таблицу `user_currency`.

## Цель работы

- Реализовать CRUD (Create, Read, Update, Delete) для сущностей бизнес-логики.
- Освоить работу с SQLite в памяти через `sqlite3`.
- Понять роль первичных и внешних ключей в связях между таблицами.
- Разделить контроллеры БД и контроллеры рендеринга страниц.
- Реализовать архитектуру MVC с чётким разделением ответственности.
- Отображать таблицу валют, на которые подписан пользователь.
- Реализовать роутер на GET-запросах с сохранением/обновлением данных.
- Протестировать функционал через `unittest.mock`.

## Структура проекта

```
lab9_currency/
├── myapp.py                     # точка входа: HTTP-сервер и роутер (do_GET)
├── models/
│   ├── __init__.py
│   ├── author.py                 # модель Author (имя, группа)
│   ├── currency.py                # модель Currency (курс валюты)
│   └── user.py                    # модель User (пользователь)
├── controllers/
│   ├── __init__.py
│   ├── databasecontroller.py      # работа с SQLite: схема + CRUD SQL-запросы
│   ├── currencycontroller.py      # бизнес-логика валют (использует CRUD)
│   ├── usercontroller.py          # бизнес-логика пользователей и подписок
│   └── pages.py                   # рендеринг страниц через Jinja2 (View-слой)
├── templates/
│   ├── index.html                 # главная страница
│   ├── author.html                # об авторе
│   ├── users.html                 # список пользователей
│   ├── user.html                  # один пользователь + его подписки
│   └── currencies.html            # список валют + формы обновления/удаления
└── tests/
    ├── __init__.py
    ├── test_models.py             # валидация моделей
    ├── test_currency_controller.py # бизнес-логика валют на unittest.mock
    ├── test_user_controller.py     # бизнес-логика пользователей на unittest.mock
    └── test_database_controller.py # интеграционные тесты реального SQLite
```

## Модели и их связи

- **Author** — автор работы: `name` (≥2 символов), `group` (>5 символов).
  Валидация выполняется в сеттерах, атрибуты приватные (`__name`, `__group`).
- **Currency** — курс валюты: `num_code`, `char_code` (ровно 3 символа,
  приводится к верхнему регистру), `name`, `value` (не может быть
  отрицательным), `nominal`.
- **User** — пользователь: `id`, `name` (≥2 символов).

Связь между `User` и `Currency` — «многие ко многим» через таблицу
`user_currency`, где `user_id` и `currency_id` — внешние ключи (`FOREIGN KEY`).

### Схема базы данных

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE currency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_code TEXT NOT NULL,
    char_code TEXT NOT NULL,
    name TEXT NOT NULL,
    value FLOAT,
    nominal INTEGER
);

CREATE TABLE user_currency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    currency_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(currency_id) REFERENCES currency(id)
);
```

**Первичный ключ (PRIMARY KEY)** однозначно идентифицирует запись в
таблице и гарантирует уникальность строк. **Внешний ключ (FOREIGN KEY)**
связывает запись одной таблицы с записью другой, обеспечивая ссылочную
целостность — например, не даёт подписать пользователя на
несуществующую валюту.

## CRUD для Currency (`controllers/databasecontroller.py`)

Все запросы параметризованы (`?` или именованные `:param`) — это
защищает от SQL-инъекций.

```python
# Create
sql = ("INSERT INTO currency(num_code, char_code, name, value, nominal) "
       "VALUES(:num_code, :char_code, :name, :value, :nominal)")
cursor.executemany(sql, data)

# Read (по коду)
cursor.execute("SELECT * FROM currency WHERE char_code = ?", (char_code,))

# Update
cursor.execute("UPDATE currency SET value = ? WHERE char_code = ?", (value, char_code))

# Delete
cursor.execute("DELETE FROM currency WHERE id = ?", (currency_id,))
```

## Маршруты приложения

| Маршрут | Описание | Шаблон |
|---|---|---|
| `/` | Главная страница: автор + список валют | `index.html` |
| `/author` | Информация об авторе | `author.html` |
| `/users` | Список пользователей | `users.html` |
| `/user?id=...` | Просмотр одного пользователя и его подписок | `user.html` |
| `/currencies` | Список всех валют | `currencies.html` |
| `/currency/delete?id=...` | Удаление валюты | — (редирект на `currencies.html`) |
| `/currency/update?char_code=USD&value=...` | Обновление курса валюты | — (редирект на `currencies.html`) |
| `/currency/show` | Вывод валют в консоль сервера (отладка) | — |

## Запуск

```bash
cd lab9_currency
python myapp.py
# сервер поднимется на http://localhost:8080/
```

При старте база заполняется демонстрационными данными: 4 валюты
(USD, EUR, GBP, AUD) и 3 пользователя с подписками на некоторые из них.

## Тестирование

```bash
python -m unittest discover -s tests -v
```

27 тестов:
- `test_models.py` — валидация свойств моделей (`ValueError` на некорректных данных).
- `test_currency_controller.py` / `test_user_controller.py` — бизнес-логика
  изолирована от БД через `unittest.mock.MagicMock`: проверяется, что
  контроллер вызывает нужные методы CRUD-слоя с правильными аргументами.
- `test_database_controller.py` — интеграционные тесты на реальной
  SQLite `:memory:`: CRUD, JOIN по внешнему ключу, устойчивость к
  попытке SQL-инъекции через параметризованный запрос.

Пример теста с моком:

```python
def test_list_currencies(self):
    mock_db = MagicMock()
    mock_db._read.return_value = [{"id": 1, "char_code": "USD", "value": 90}]
    controller = CurrencyController(mock_db)
    result = controller.list_currencies()
    self.assertEqual(result[0]["char_code"], "USD")
    mock_db._read.assert_called_once_with()
```

Результат прогона:

```
Ran 27 tests in 0.004s

OK
```

## Архитектура MVC

- **Model** (`models/`) — только данные и их валидация (свойства,
  геттеры/сеттеры), без обращения к БД.
- **Controller** — разделён на два слоя:
  - `databasecontroller.py` — единственное место, где выполняются
    SQL-запросы к SQLite;
  - `currencycontroller.py` / `usercontroller.py` — бизнес-логика,
    которая обращается к CRUD-слою, а не к SQL напрямую;
  - `pages.py` — готовит контекст для шаблонов и рендерит HTML через
    Jinja2 `Environment`, созданный один раз в `myapp.py` и
    переиспользуемый всеми страницами.
- **View** (`templates/`) — HTML-шаблоны Jinja2, не содержат логики
  доступа к данным, только отображение переданного контекста.
- `myapp.py` — точка сборки: создаёт `Environment`, контроллеры,
  заполняет БД демо-данными и запускает `HTTPServer` с роутингом в
  `do_GET`.

## Выводы

Применение архитектуры MVC позволило чётко разграничить
ответственность между слоями: модели отвечают только за валидацию
данных предметной области, слой доступа к БД — единственное место
исполнения SQL, бизнес-логика контроллеров не знает деталей SQL, а
шаблоны Jinja2 полностью изолированы от логики приложения. Работа с
SQLite в памяти (`:memory:`) через параметризованные запросы защищает
от SQL-инъекций и упрощает тестирование — каждый тест создаёт свежую
базу без побочных эффектов на диске. Использование `unittest.mock`
позволило протестировать бизнес-логику контроллеров в изоляции от
БД, а `http.server` с простым роутером на `do_GET` оказался
достаточным для реализации полноценного набора маршрутов с GET-based
CRUD-операциями и рендерингом Jinja2-шаблонов.
