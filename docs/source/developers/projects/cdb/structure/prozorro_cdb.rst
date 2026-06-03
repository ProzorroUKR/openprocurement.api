.. _cdb_structure_prozorro_cdb:

Асинхронний підпроект: ``prozorro_cdb``
========================================

Стек: **aiohttp + motor (async pymongo) + pydantic**.
Новий асинхронний API, що розробляється паралельно з ``openprocurement``.

Коренева директорія: ``src/prozorro_cdb/``

.. note::

   Підпроект є функціональним дзеркалом ``openprocurement``.
   При внесенні глобальних змін (БД, фід, auth, middleware) — їх треба вносити **в обидва підпроекти**.

Інфраструктурний пакет ``api/``
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Файл / директорія
     - Призначення
   * - ``application.py``
     - Ініціалізація aiohttp-додатку; підключення middleware і routes
   * - ``database/store.py``
     - ``MongodbStore`` (async/motor), ``BaseCollection``, ``atomic_transaction_async``; логіка фіду (``list()``), ``save_data()``, watermark
   * - ``database/schema/``
     - Pydantic-схеми для документів у MongoDB: ``common.py``, ``document.py``, ``organization.py``
   * - ``context.py``
     - Контекст запиту на базі ``contextvars`` (``get_now_async``, ``url_to_absolute``)
   * - ``auth.py``
     - Автентифікація брокерів і сервісних токенів (async)
   * - ``handlers/base.py``
     - ``BaseView`` (PydanticView), ``parse_offset``, ``compose_offset``; логіка пагінації фіду
   * - ``handlers/schema/``
     - Pydantic-схеми для запитів і відповідей: ``feed.py``, ``document.py``, ``common.py``
   * - ``serializers/``
     - Серіалізатори відповідей (``base.py``, ``document.py``, ``organization.py``)
   * - ``state/base.py``
     - ``BaseState``: хук ``create_document_objects``; бізнес-логіка переходів
   * - ``middlewares.py``
     - aiohttp-middleware (таймінги, логування, сесія БД)
   * - ``migrations/utils.py``
     - Утиліти для написання міграцій
   * - ``settings.py``
     - Конфігурація додатку (читається з env / ini)
   * - ``storage.py``
     - Завантаження документів у Document Storage

Глобальні pytest-фікстури (при появі тестів): ``src/prozorro_cdb/conftest.py``

Доменні пакети
--------------

Кожен домен — окремий пакет: ``tender/``, ``contracting/``, ``framework/``, ``violation_report/``.

Структура всередині кожного домену:

.. code-block:: text

   <domain>/
   ├── core/
   │   ├── database.py    # BaseCollection для домену (колекція, індекси)
   │   └── initialize.py  # Реєстрація колекції в MongodbStore при старті
   ├── handlers/          # aiohttp handlers (GET list, GET item, POST, PATCH)
   │   └── schema/        # Pydantic-схеми вхідних/вихідних даних
   ├── database/          # (якщо потрібні додаткові схеми або helpers)
   │   └── schema/
   ├── serializers/       # серіалізатори відповідей
   ├── state/             # бізнес-логіка переходів станів
   └── migrations/        # міграції даних (нумеровані, 0001_…)

.. note::

   ``violation_report`` — найбільш повно реалізований домен і є зразком для нових доменів.

Відповідності з ``openprocurement``
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 40 20

   * - ``openprocurement``
     - ``prozorro_cdb``
     - Різниця
   * - ``api/database.py``
     - ``api/database/store.py``
     - async/motor
   * - ``procedure/views/``
     - ``handlers/``
     - PydanticView замість Pyramid
   * - ``procedure/models/`` (schematics)
     - ``database/schema/`` + ``handlers/schema/`` (pydantic)
     - розділені DB-схема і API-схема
   * - ``procedure/state/``
     - ``state/``
     - async методи
   * - ``procedure/serializers/``
     - ``serializers/``
     - аналогічно
   * - ``api/views/base.py``
     - ``api/handlers/base.py``
     - аналогічна логіка offset/пагінації

Правила розміщення коду
-----------------------

- **Бізнес-логіка** → ``state/``; state-класи не роблять запити до БД напряму
- **Запити до БД** → лише з ``handlers/`` (через ``MongodbStore.get_instance().<collection>``)
- **Схема вхідних даних (API)** → ``handlers/schema/`` (pydantic)
- **Схема документа в БД** → ``database/schema/`` (pydantic)
- **Серіалізація відповіді** → ``serializers/``
- **Реєстрація колекції** → ``<domain>/core/initialize.py`` (викликається при старті aiohttp)
- **Зміна схеми / даних у БД** → ``migrations/`` (нумеровані файли)
