
.. _qualification_requirement_response_operation:

Відповідь на вимогу в пре-кваліфікації
--------------------------------------

Будь-які дії над відповіддю на вимогу в пре-кваліфікації може виконувати лише замовник.

Базові операції над відповідями на вимоги
-----------------------------------------

Схема даних :ref:`відповіді на вимогу<RequirementResponse>`


Створення відповіді на вимогу
"""""""""""""""""""""""""""""

Можливо створити декілька відповідей на вимоги за один запит з повним набором даних.

.. http:example:: http/criteria/qualification-create-requirement-response.http
   :code:

Можливо також створювати відповіді на вимоги одним запитом через оновлення пре-кваліфікації.

.. http:example:: http/criteria/add-requirement-response-from-qualification.http
   :code:


Оновлення відповіді на вимогу
"""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-update-requirement-response.http
   :code:

Можливо редагувати відповіді на вимоги одним запитом через оновлення пре-кваліфікації, але потрібно передавати також всі відповіді на вимоги, або відповіді, які не будуть передані - будуть видалені.

.. http:example:: http/criteria/patch-requirement-response-from-qualification.http
   :code:


Отримання інформації по відповіді на вимогу
"""""""""""""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-requirement-response-list.http
   :code:

.. http:example:: http/criteria/qualification-requirement-response.http
   :code:


Видалення відповіді на вимогу
"""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-delete-requirement-response.http
   :code:


Базові операції над доказами
----------------------------

Схема даних :ref:`доказу<evidence>`

Створення Доказу
""""""""""""""""

.. http:example:: http/criteria/qualification-create-requirement-response-evidence.http
   :code:


Оновлення доказу
""""""""""""""""

.. http:example:: http/criteria/qualification-update-requirement-response-evidence.http
   :code:

Отримання інформації по доказу
""""""""""""""""""""""""""""""

.. http:example:: http/criteria/qualification-requirement-response-evidence-list.http
   :code:

.. http:example:: http/criteria/qualification-requirement-response-evidence.http
   :code:

Видалення доказу
""""""""""""""""

.. http:example:: http/criteria/qualification-delete-requirement-response-evidence.http
   :code:
