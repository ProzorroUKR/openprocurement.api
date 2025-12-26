
.. _bid_requirement_response_operation:

Відповідь на вимогу в пропозиції
--------------------------------

Відповідь на вимогу - об'єкт який показує що користувач відповідає вимогам замовника, та може приймати участь у закупівлі.

Будь-які дії над відповіддю на вимогу в пропозиції може виконувати лише власник пропозиції.

Базові операції над відповідями на вимоги
-----------------------------------------

Схема даних :ref:`відповіді на вимогу<RequirementResponse>`

Створення відповіді на вимогу
"""""""""""""""""""""""""""""

Можливо створити декілька відповідей на вимоги за один запит з повним набором даних.

.. http:example:: http/criteria/create-requirement-response.http
   :code:

Можливо також створювати відповіді на вимоги одним запитом через оновлення пропозиції.

.. http:example:: http/criteria/add-requirement-response-from-bid.http
   :code:


Оновлення відповіді на вимогу
"""""""""""""""""""""""""""""

.. http:example:: http/criteria/update-requirement-response.http
   :code:

Можливо редагувати відповіді на вимоги один запитом через оновлення пропозиції, але потрібно передавати також всі відповіді на вимоги, або віповіді, які не будуть передані - будуть видалені.

.. http:example:: http/criteria/patch-requirement-response-from-bid.http
   :code:


Отримання інформації по відповіді на вимогу
"""""""""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/requirement-response-list.http
   :code:

.. http:example:: http/criteria/requirement-response.http
   :code:


Видалення відповіді на вимогу
"""""""""""""""""""""""""""""

.. http:example:: http/criteria/delete-requirement-response.http
   :code:

Можливо видалити відповіді на вимогу за один запит через оновлення пропозиції, просто не передавши ці відповіді.

.. http:example:: http/criteria/update-requirement-response.http
   :code:


Базові операції над доказами
----------------------------

Схема даних :ref:`доказу<evidence>`

Створення Доказу
""""""""""""""""

.. http:example:: http/criteria/create-requirement-response-evidence.http
   :code:


Оновлення доказу
""""""""""""""""

.. http:example:: http/criteria/update-requirement-response-evidence.http
   :code:

Отримання інформації по доказу
""""""""""""""""""""""""""""""

.. http:example:: http/criteria/requirement-response-evidence-list.http
   :code:

.. http:example:: http/criteria/requirement-response-evidence.http
   :code:

Видалення доказу
""""""""""""""""

.. http:example:: http/criteria/delete-requirement-response-evidence.http
   :code:

.. _bid_activation_with_requirement_responses:

Активація пропозіції
--------------------

Коли пропозіція переходить до стаусу `active`/`pending` або оновлюється в цих статусах, спрацьoвує валідація яка перевіряє відповідність відповідей та критерій.

Відповіді обов'язкові лише для критеріїв, які мають хоча б одину вимогу у статусі `active`.

Помилка, коли в пропозіції немає відповідей на один з критеріїв:

.. http:example:: http/criteria/requirement-response-basic-data-1.http
   :code:

.. http:example:: http/criteria/bid-activation-not-all-criteria.http
   :code:

Помилка, коли в пропозиції існують відповіді на декілька груп вимог в рамках одного критерію:

.. http:example:: http/criteria/requirement-response-basic-data-2.http
   :code:

.. http:example:: http/criteria/bid-activation-answered-on-two-groups.http
   :code:


Помилка, коли пропозиція не містить відповіді хоча б на одну вимогу в рамках однієї групи вимог:

.. http:example:: http/criteria/requirement-response-basic-data-3.http
   :code:

.. http:example:: http/criteria/bid-activation-not-all-requirements.http
   :code:


Схема роботи відповідей на вимогу
---------------------------------

Схему роботу ви можете побачити тут: :ref:`Схема роботи <criteria_workflow>`