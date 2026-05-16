.. _cdb_structure_openprocurement:

Синхронний підпроект: ``openprocurement``
=========================================

Стек: **Pyramid + pymongo + schematics**.
Основний продакшн API із повною функціональністю.

Коренева директорія: ``src/openprocurement/``

Інфраструктурний пакет ``api/``
--------------------------------

Містить увесь базовий рівень, від якого успадковуються всі доменні пакети.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Файл / директорія
     - Призначення
   * - ``app.py``
     - Ініціалізація Pyramid-додатку; підключення всіх includeme
   * - ``database.py``
     - ``MongodbStore``, ``BaseCollection``, ``atomic_transaction``; логіка фіду (``list()``), ``save_data()``, watermark
   * - ``context.py``
     - Thread-local контекст запиту (``get_request``, ``set_request_now``, ``get_db_session``)
   * - ``auth.py``
     - Автентифікація брокерів і сервісних токенів
   * - ``constants.py`` / ``constants_env.py``
     - Бізнес-константи та константи з env-змінних (``FEED_WATERMARK_SECONDS`` тощо)
   * - ``utils.py``
     - Спільні утиліти: ``context_unpack``, ``raise_operation_error``, ``json_view``, ``update_logging_context``
   * - ``validation.py``
     - Декоратори валідації запитів
   * - ``middlewares.py``
     - WSGI-middleware (таймінги, логування)
   * - ``views/base.py``
     - ``BaseResource``, ``MongodbResourceListing``; парсинг та формування offset; логіка пагінації фіду
   * - ``procedure/models/``
     - Базові schematics-моделі: ``Address``, ``Document``, ``Organization``, ``Period``, ``Value`` тощо
   * - ``procedure/state/base.py``
     - ``BaseState``: хуки ``on_post`` / ``on_patch`` / ``always``; ``status_up``
   * - ``procedure/serializers/``
     - Базові серіалізатори відповідей
   * - ``procedure/views/``
     - *(порожньо на рівні api; конкретні views — в доменних пакетах)*
   * - ``migrations/``
     - Базова інфраструктура міграцій (``base.py``, ``rename.py``)
   * - ``tests/``
     - Базові утиліти для тестів: ``base.py``, ``mock.py``, ``utils.py``

Глобальні pytest-фікстури: ``src/openprocurement/conftest.py``

Доменні пакети
--------------

Кожен домен — окремий пакет: ``tender/``, ``contracting/``, ``framework/``, ``planning/``, ``relocation/``, ``historical/``.

Всередині кожного домену:

- ``core/`` — спільна логіка для всіх типів процедур домену
- Конкретні типи процедур (``belowthreshold/``, ``open/``, ``contract/`` тощо)

Структура всередині кожного типу процедури:

.. code-block:: text

   <domain>/<type>/
   ├── procedure/
   │   ├── models/       # schematics-моделі об'єктів (Tender, Contract, Bid тощо)
   │   ├── state/        # бізнес-логіка переходів станів
   │   ├── views/        # Pyramid-в'юхи (GET, POST, PATCH)
   │   └── serializers/  # серіалізатори відповідей
   ├── migrations/       # міграції даних у MongoDB (нумеровані, 0001_…)
   └── tests/            # інтеграційні тести

Правила розміщення коду
-----------------------

- **Бізнес-логіка** → ``procedure/state/``; state-класи не роблять запити до БД напряму
- **Запити до БД** → лише з ``procedure/views/`` (через ``request.registry.mongodb.<collection>``)
- **Валідація вхідних даних** → ``procedure/models/`` (schematics) і ``validation.py``
- **Серіалізація відповіді** → ``procedure/serializers/``
- **Зміна схеми / даних у БД** → ``migrations/`` (не в коді ініціалізації)
- **Спільні утиліти домену** → ``<domain>/core/``
- **Глобальні константи з часовою прив'язкою** → ``constants_env.py`` (читаються з env або ``constants.ini``)
