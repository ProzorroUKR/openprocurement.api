.. _restricted:

restricted
==========

Процедура закупівлі з обмеженим доступом
----------------------------------------

Поле `restricted` є булевим полем, яке вказує, чи має тендер обмежений доступ.

Створимо тендер з конфігурацією `restricted=false`:

.. http:example:: http/restricted-false-tender-post.http
   :code:

Після активації зробимо анонімний get запит:

.. http:example:: http/restricted-false-tender-get-anon.http
   :code:

Ми бачимо, що цей тендер має звичайне представлення.

Тепер створимо тендер з конфігурацією `restricted=true`:

.. http:example:: http/restricted-true-tender-post.http
   :code:

Після активації зробимо анонімний get запит:

.. http:example:: http/restricted-true-tender-get-anon.http
   :code:

Тепер ми бачимо, що деякі поля приховані.

Але якщо ми зробимо запит з `broker` токеном, ми побачимо, що відповідні поля більше не приховані:

.. http:example:: http/restricted-true-tender-get.http
   :code:

Давайте подивимось на ці 2 тендери в стрічці.

Через анонімний запит:

.. http:example:: http/restricted-tender-feed-anon.http
   :code:

Через запит майданчика:

.. http:example:: http/restricted-tender-feed.http
   :code:

Ми також бачимо, що `restricted=true` тендер прихований для анонімного запиту, але не для запиту майданчика.

Договір з обмеженим доступом
----------------------------

Для тендеру з `restricted=true` буде створено договір з `restricted=true`.

Отримаємо обмежений договір через анонімний запит:

.. http:example:: http/restricted-true-contract-get-anon.http
   :code:

Ми бачимо, що деякі поля приховані.

Але якщо ми зробимо запит з `broker` токеном, ми побачимо, що відповідні поля більше не приховані:

.. http:example:: http/restricted-true-contract-get.http
   :code:

Правила приховування
--------------------

.. note::
    Правила створюються з JSONPath виразів. Для отримання додаткової інформації читайте `JSONPath specification <https://goessner.net/articles/JsonPath/>`_.

Правила приховування закупівлі:

.. csv-table::
   :file: csv/tender-mask-mapping.csv
   :header-rows: 1

Правила приховування договору:

.. csv-table::
   :file: csv/contract-mask-mapping.csv
   :header-rows: 1
