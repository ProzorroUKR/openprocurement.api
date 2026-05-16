.. _cdb_feed_ordering:

Гарантія порядку в API фіді
============================

Use case
--------

API надає фід — посторінковий перелік об'єктів (тендерів, договорів тощо), відсортованих від старіших до новіших або навпаки.
Зовнішні системи (crawler-и, databridge-и) синхронізуються через цей фід: кожен клієнт зберігає власний ``offset`` і з ним повертається до API за наступною порцією даних.

Відповідь містить ``next_page`` з ``offset`` для наступного запиту:

.. code-block:: json

   {
       "data": [
           {"dateModified": "2026-05-12T14:00:00.396982+03:00", "id": "5d1a99de..."},
           {"dateModified": "2026-05-12T14:00:00.405816+03:00", "id": "7e04e10d..."},
           {"dateModified": "2026-05-12T14:00:00.422566+03:00", "id": "ddf6f769..."}
       ],
       "next_page": {
           "offset": "1778583600.49.1.3c7bb878...",
           "path": "/api/2.5/tenders?limit=1000&offset=1778583600.49.1.3c7bb878...",
           "uri": "https://public-api.prozorro.gov.ua/api/2.5/tenders?limit=1000&offset=1778583600.49.1.3c7bb878..."
       }
   }

Offset кодує значення поля ``public_modified`` останнього елемента сторінки + кількість і хеш елементів з таким самим значенням (для обробки колізій). Наступний запит повертає тільки об'єкти з ``public_modified`` більшим за цей offset.

Поле ``public_modified`` встановлюється при кожному записі об'єкта в БД через MongoDB aggregation pipeline:

.. code-block:: python

   # src/openprocurement/api/database.py
   def get_public_modified():
       public_modified = {"$divide": [{"$toLong": "$$NOW"}, 1000]}
       return public_modified

``$$NOW`` — системна змінна MongoDB, що повертає поточний час **на початку операції** (в мілісекундах).

Проблема: race condition в порядку public_modified
--------------------------------------------------

``$$NOW`` фіксує час на початку операції, а не в момент її коміту в базу.
При паралельних записах операції можуть закомітитись не в тому порядку, в якому вони стартували.

**Приклад:**

.. code-block::

   T=489ms  Операція A стартує → $$NOW → public_modified = 1778583600.489
   T=490ms  Операція B стартує → $$NOW → public_modified = 1778583600.490
             Операція B комітить першою (менша/простіша обробка)
   T=495ms  Операція A комітить другою

Клієнт читає фід між T=490ms і T=495ms:

- бачить об'єкт B з ``public_modified = 1778583600.490``
- отримує ``next_page offset = 1778583600.490``
- об'єкт A ще не закомітився → не потрапляє на сторінку

Після T=495ms об'єкт A з'являється в базі з ``public_modified = 1778583600.489``.
Але клієнт вже має ``offset = 1778583600.490``, а наступний запит фільтрує ``public_modified > 1778583600.490``.
Об'єкт A (``0.489 < 0.490``) **назавжди пропускається** клієнтом.

Причини чому операції комітять не по порядку:

- різна тривалість обробки (більше вкладених документів, валідацій)
- очікування на lock іншого документа
- read preference secondary + replication lag

.. note::

   Поле ``public_ts``, яке встановлюється через ``$$CLUSTER_TIME``, має **ту саму проблему**: ``$$CLUSTER_TIME`` так само фіксується на початку операції, а не при коміті. Монотонний порядок видимості гарантує лише oplog ``ts``, але отримати його у рамках того ж запису неможливо.

Рішення: Watermark delay
-------------------------

Фід не видає об'єкти, ``public_modified`` яких молодший за ``N`` секунд від поточного часу MongoDB.
За цей час усі паралельні транзакції зі схожими timestamps встигають закомітитись і стати видимими.

Ключовий момент: watermark рахується за допомогою ``$$NOW`` **самої MongoDB**, а не ``time.time()`` на API сервері.
Це виключає проблему розсинхронізації годинників між API сервером і MongoDB.

**Реалізація в** ``src/openprocurement/api/database.py``, метод ``list()``:

.. code-block:: python

   FEED_WATERMARK_SECONDS = int(os.environ.get("FEED_WATERMARK_SECONDS", "1"))

   def list(self, collection, fields, ..., descending=False, offset_value=None, ...):
       ...
       if offset_value:
           suffix = "e" if inclusive_filter else ""
           operator = "$lt" if descending else "$gt"
           filters[offset_field] = {operator + suffix: offset_value}

       if offset_field == "public_modified" and FEED_WATERMARK_SECONDS > 0 and (not descending or not offset_value):
           filters["$expr"] = {
               "$lte": [
                   f"${offset_field}",
                   {
                       "$subtract": [
                           {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                           FEED_WATERMARK_SECONDS,
                       ]
                   },
               ]
           }
       ...

Watermark застосовується у двох випадках:

- **Forward feed** (без ``descending``) — завжди. Не дає crawler-у просунути offset
  за записи, що ще не закомітились.
- **Descending без offset** (перша сторінка) — щоб offset першої сторінки,
  який клієнт використовує як точку розвороту для forward sync, був достатньо старим.
  Всі паралельні записи, чий ``$$NOW`` менший за цей offset, встигають закомітитись
  за час watermark. Без цього backward→forward sync може назавжди пропустити записи,
  що були in-flight під час початкового descending-читання.
- **Descending з offset** — watermark **не застосовується**. Клієнт пагінує
  по історичних даних, там race condition неможливий.

.. note::

   Значення ``FEED_WATERMARK_SECONDS`` має бути більшим за максимально можливу затримку між стартом і комітом операції запису.
   Рекомендоване значення: **1 секунда**.

   ``$$NOW`` фіксується вже на стороні MongoDB — мережева затримка між API сервером і MongoDB на race window не впливає.
   Реальний race window визначається лише MongoDB-internal затримками:

   - lock contention на стороні MongoDB
   - replication latency до secondary-реплік (majority write concern)

   За результатами навантажувального тесту максимальна затримка між ``$$NOW`` і комітом склала **37 мс**.
   1 секунда дає ~27-кратний запас відносно реально спостережуваного максимуму.
   Значущі перевищення можливі лише під час MongoDB election (failover), коли writes можуть затримуватись на секунди —
   але в такому сценарії клієнти і так отримують помилки з'єднання.

   Значення можна перевизначити через змінну середовища ``FEED_WATERMARK_SECONDS``.

Альтернатива: Change Streams як pull feed
-----------------------------------------

MongoDB Change Streams — це API поверх oplog, що дозволяє отримувати події змін (insert, update, delete) у гарантованому порядку коміту.
Кожна подія має **resume token** — непрозорий вказівник на позицію в oplog. Він стає offset-ом клієнта замість ``public_modified``.

.. code-block::

   Клієнт: GET /tenders               → resume_token_A  (next_page offset)
   Клієнт: GET /tenders?offset=token_A → resume_token_B
   Клієнт: GET /tenders?offset=token_B → ...

Реалізація на стороні API — при кожному запиті відкривається change stream з ``resumeAfter: <token>``,
читається ``limit`` подій, повертаються документи і новий token:

.. code-block:: python

   with collection.watch(resume_after=resume_token, full_document="updateLookup") as stream:
       for event in stream:
           if event["operationType"] in ("insert", "update", "replace"):
               results.append(event["fullDocument"])
               last_token = stream.resume_token
           if len(results) >= limit:
               break

Порядок гарантований: resume token базується на oplog ``ts``, який є монотонним і відповідає реальному порядку коміту.
Проблема race condition відсутня — якщо операція A закомітилась після B, її token буде більшим за token B.

**Обмеження підходу:**

- **Немає descending**: oplog читається лише вперед. Зворотний порядок потребує окремого механізму.
- **Oplog window**: resume token стає недійсним, якщо oplog вже "прокрутився" (capped collection). Клієнт, що давно не синхронізувався, втрачає позицію і мусить починати з початку.
- **Події, а не стан**: якщо об'єкт оновлювався 10 разів між двома запитами клієнта, він отримає 10 подій з ``full_document`` на кожну. При ``updateLookup`` документ підвантажується окремим запитом до колекції, що підвищує навантаження.
- **Відкриття stream на кожен HTTP запит**: change stream — це persistent cursor в MongoDB. Відкривати і закривати його на кожен запит дорого. Потребує або server-sent events / websockets, або кешування курсора між запитами.

Альтернатива: Oplog Tailer
--------------------------

Окремий сервіс слідкує за oplog через change stream і проставляє кожному документу поле ``committed_ts`` —
реальний oplog ``ts`` моменту коміту. Це єдине поле, що відображає справжній порядок видимості в БД.

.. code-block::

   ┌─────────────┐  write   ┌──────────┐  oplog   ┌───────────────┐
   │  API Server │ ───────→ │ MongoDB  │ ────────→ │  Oplog Tailer │
   └─────────────┘          └──────────┘           └───────┬───────┘
                                  ↑                        │
                                  │   $set committed_ts    │
                                  └────────────────────────┘

.. code-block:: python

   # oplog tailer
   with db["tenders"].watch(full_document="updateLookup") as stream:
       for event in stream:
           oplog_ts = event["clusterTime"]   # реальний ts коміту з oplog
           collection.update_one(
               {"_id": event["documentKey"]["_id"]},
               {"$set": {"committed_ts": oplog_ts}},
           )

Фід API сортує і фільтрує по ``committed_ts``. Порядок гарантований — ``committed_ts`` присвоюється
вже після коміту і збігається з порядком oplog.

**Обмеження підходу:**

- **Затримка між записом і видимістю у фіді**: документ з'являється у фіді лише після того, як tailer обробив подію і проставив ``committed_ts``. Зазвичай це десятки мілісекунд, але при відставанні tailer-а може зрости.
- **Додатковий write на кожну зміну**: tailer робить ``update_one`` для кожного запису в колекції, що вдвічі збільшує кількість writes.
- **Окремий сервіс**: потребує деплою, моніторингу, обробки падінь і відновлення позиції після рестарту (збереження resume token).
- **Але**: descending підтримується, oplog window не є проблемою (документ вже має ``committed_ts``), клієнти використовують звичайний ``find()`` по індексу.

.. warning::

   **Циклічний update.** ``update_one`` від tailer-а сам потрапляє в oplog і генерує нову подію в change stream,
   яку tailer знову обробляє — і так до нескінченності. Перед реалізацією необхідно передбачити розрив циклу,
   наприклад через фільтр у watch pipeline що ігнорує події де змінилось тільки ``committed_ts``,
   або через винесення ``committed_ts`` в окрему колекцію ``tenders_feed``.

Порівняння підходів
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 20 30

   * - Підхід
     - Гарантія порядку
     - Descending
     - Складність
   * - ``public_modified`` без watermark
     - Ні (race condition)
     - Так
     - —
   * - ``public_modified`` + watermark (``$$NOW``)
     - Практична (~100%)
     - Так
     - Мінімальна
   * - Change streams як pull feed
     - Так
     - Ні
     - Висока
   * - Oplog tailer + ``committed_ts``
     - Так
     - Так
     - Висока (окремий сервіс)

Watermark через ``$$NOW`` MongoDB обрано як прагматичне рішення:
воно вирішує проблему race condition без зміни архітектури і без додаткових сервісів.

Підтвердження проблеми: результати навантажувального тесту
----------------------------------------------------------

Проблему підтверджено експериментально. Навантажувальний тест знаходиться в
``loadtesting/feed_ordering.py``.

**Умови тесту:**

- Тривалість: ~4.5 хвилини
- 70 малих тендерів (1 item) + 70 великих тендерів (10 items з довгими описами)
- Інтенсивність оновлень: ~72 PATCH/сек (36.8 small + 35.2 large)
- Загальна кількість оновлень: ~12 700 small + ~11 900 large = ~24 600 patches
- Перевірок фіду: 488

**Результати:**

.. code-block::

   DETECT feed ordering check
   Total requests:  488
   Failures:         11  (2.25%)

11 з 488 перевірок зафіксували тендери, які з'явились всередині вже відпрацьованого
вікна ``public_modified`` — тобто були б назавжди пропущені реальним crawler-ом.

**Величина затримки** (``pm_max - late_arrival.public_modified``):

.. code-block::

   Мінімальна:  1 мс
   Максимальна: 37 мс
   Середня:     12.5 мс
   Всі значення (мс): 24, 1, 17, 3, 37, 13, 22, 4, 4, 11, 2

Тобто достатньо щоб одна транзакція випередила іншу лише на **1–37 мілісекунд**,
щоб об'єкт назавжди випав з фіду. При навантаженні 72 оновлень/сек такі колізії
виникають регулярно.

**Приклад зафіксованої аномалії:**

.. code-block::

   ANOMALY DETECTED  2026-05-16T09:15:54
   Feed window:  public_modified [1778922858.024 … 1778922950.934]

   SNAPSHOT 1 (was):
     1778922950.934  b3792567814f4bfabadb585289ea3c5f   ← newest
     1778922950.916  2e8ed7fd61994e2ea956f11a654c6e8a
     ...

   LATE ARRIVALS:
     >>> 1778922950.910  4b4711e117bd4454a233b5bcb6259197

   Тендер 4b47... отримав $$NOW = 1778922950.910 (на 24мс раніше за останній),
   але закомітився після того як snapshot_1 вже був знятий.
   Crawler з offset=1778922950.934 ніколи не побачить цей тендер.
