.. _has_awarding_order:

hasAwardingOrder
================

Поле `hasAwardingOrder` є булевим полем, яке вказує, чи буде застосований спосіб ранжування пропозицій, вказаний в awardCriteria під час їх розкриття, і пропозиції будуть створюватися по черзі чи всі пропозиції створюються одночасно.

Можливі значення для поля `hasAwardingOrder` залежать від поля `procurementMethodType`:

.. csv-table::
   :file: csv/has-awarding-order-values.csv
   :header-rows: 1

hasAwardingOrder встановлено у `true`
-------------------------------------

Створимо тендер з `hasAwardingOrder` встановленим у `true`:

.. http:example:: http/has-awarding-order-true-tender-post.http
   :code:

Ви можете зазначити тип awardCriteria під час створення тендеру з `hasAwardingOrder` встановленим у `true`:
    * lowestCost
    * lifeCycleCost
    * ratedCriteria

Додамо лот до тендера:

.. http:example:: http/has-awarding-order-true-tender-add-lot.http
   :code:

Подивимося на тендер з результатами аукціону:

.. http:example:: http/has-awarding-order-true-auction-results.http
   :code:

Це звичайний флоу зі створенням авардів по черзі завдяки сортуванню за критерієм (awardCriteria). Другий авард (для тендеру/лота) буде згенерований, якщо замовник скасовує рішення щодо першого згенерованого аварду.

hasAwardingOrder встановлено у `false`
--------------------------------------

Тепер створимо тендер з `hasAwardingOrder` встановленим у `false`:

.. http:example:: http/has-awarding-order-false-tender-post.http
   :code:

Додамо лот до тендера:

.. http:example:: http/has-awarding-order-false-tender-add-lot.http
   :code:

Подивимося на тендер з результатами аукціону:

.. http:example:: http/has-awarding-order-false-auction-results.http
   :code:

Усі аварди були згенеровані одразу після завершення аукціону. Після цього замовник може вибрати будь-яку пропозицію в якості переможця.

Різниця
-------

Подивимося на різницю завершених тендерів:

.. literalinclude:: json/has-awarding-order-false-auction-results.json
   :diff: json/has-awarding-order-true-auction-results.json

Різниця для тендеру з `hasAwardingOrder` встановленим у `false` порівняно з `true` це те, що в тендері  з `hasAwardingOrder` встановленим у `false` після того, як аукціон завершується, всі пропозиції розкриваються одночасно і приймають статус pending. Потім замовниик може перевіряти отримані пропозиції послідовно або в тому порядку, в якому він вважає за потрібне.

Зміна статусів пропозицій для hasAwardingOrder = false
------------------------------------------------------
Розглянемо випадки зі зміною статусів аварду.

В якості прикладу розглянемо тендер з трьома учасниками. Створено три пропозиції зі статусом pending:

.. http:example:: http/has-awarding-order-false-auction-results-example-1.http
   :code:

1) Замовник визнає переможцем award1

.. http:example:: http/has-awarding-order-false-auction-results-example-1-activate-first-award.http
   :code:

В цьому випадку award1 стає `active`, award2 та award3 залишаються `pending`

.. http:example:: http/has-awarding-order-false-auction-results-example-1-results.http
   :code:

2) Замовник скасував своє рішення по award1

.. http:example:: http/has-awarding-order-false-auction-results-example-2-cancel-first-award.http
   :code:

В цьому випадку award1 стає `cancelled`, award2 та award3 залишаються `pending` і генерується новий award4 в статусі `pending` через те, що award1 був скасований

.. http:example:: http/has-awarding-order-false-auction-results-example-2-results.http
   :code:

3) Замовник відхиляє пропозицію award4 та визнає переможцем award2

В цьому випадку award1 залишається `cancelled`, award2 стає `active`, award3 залишається `pending`, award4 стає `unsuccessful`:

.. http:example:: http/has-awarding-order-false-auction-results-example-3-results.http
   :code:

4) Замовник скасовує своє рішення по award4

В цьому випадку award1 залишається `cancelled`, award2 - `active`, award3 - `pending`, award4 - `cancelled` і генерується новий award5 в статусі `pending` через те, що award4 був скасований:

.. http:example:: http/has-awarding-order-false-auction-results-example-4-results.http
   :code:
