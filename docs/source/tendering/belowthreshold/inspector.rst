.. _inspector_tutorial:


Туторіал Закупівля з контролером
================================


.. index:: Inspector

Створення закупівлі з контролером
---------------------------------

Для створення закупівлі з контролером потрібно передати поле `inspector` при створені або можете встановити пізніше пропатчивши закупівлю в статусі `draft` або `active.enquiries`

Поле `inspector` дозволено передавати лише разом з `funders` (в закупівлях з донором):

Ось, що станеться якщо ви спробуєте створити закупівлю з контролером без `funders`

.. http:example:: http/tutorial/tender-with-inspector-post-without-funders.http
   :code:

Ми отримали помилку 422, тепер давайте спробуємо створити закупівлю разом з полями `inspector` та `funders`:

.. http:example:: http/tutorial/tender-with-inspector-post-success.http
   :code:


Зміна контролера
----------------

Поле `inspector` може бути змінене лише в статусах `draft` та `active.enquiries`:

.. http:example:: http/tutorial/patch-tender-inspector-success.http
   :code:


Створення запиту на перевірку
-----------------------------

Запит на перевірку може створити замовник лише в закупівлі з контролером і лише в статусах `active.enquiries`, `active.qualification` (якщо закупівля мультилотова)/ `active.awarded` (якщо закупівля безлотова або з одним лотом).

.. http:example:: http/tutorial/post-tender-review-request-success.http
   :code:

В залежності від статусу від моменту створення і до моменту відповіді на запит забороняється:
    - `active.enquiries` - змінювати закупівлю(окрім `tenderPeriod`)
    - `active.qualification`/`active.awarded`` - змінювати аварди, активувати контракти


Cпробуємо змінити опис закупівлі:

.. http:example:: http/tutorial/patch-tender-with-unanswered-review-request.http
   :code:

Тепер спробуєм змінити період подання пропозиції:

.. http:example:: http/tutorial/patch-tender-period-with-review-request.http
   :code:

Новий запит на перевірку не може бути створений поки існує інший запит без відповіді

.. http:example:: http/tutorial/post-tender-review-request-already-exist.http
   :code:


Створення запиту на перевірку на етапі кваліфікації
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Якщо закупівля лотова, то при створенні запиту на перевірку потрібно вказати `lotID`:

.. http:example:: http/tutorial/post-review-request-without-lot-id.http
   :code:

Запит на перевірку на етапі кваліфікації може бути створений лише при наявності переможця.

.. http:example:: http/tutorial/post-review-request-without-active-award.http
   :code:



Відповідь контролера
--------------------

Надавати відповідь на запит перевірки може лише користувач з роллю `inspector` в системі використовуючи PATCH метод на запит:

.. http:example:: http/tutorial/patch-tender-review-request-false.http
   :code:

Контролер не може надати відповідь на один і той самий запит двічі:

.. http:example:: http/tutorial/second-patch-tender-review-request-false.http
   :code:

Закупівля не може рухатись далі по статусам поки не буде надане погодження на запит перевірки.

Тож замовнику потрібно внести зміни, створити новий запит перевірки і після цього контролер може надати повторне рішення:

.. http:example:: http/tutorial/patch-tender-review-request-true.http
   :code: