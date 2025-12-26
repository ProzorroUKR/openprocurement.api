.. _planning_tutorial:

Туторіал
========

Створення плану закупівлі
-------------------------

Наполегливо рекомендуємо створювати плани у статусі `draft`.

Створимо план:

.. http:example:: tutorial/create-plan.http
   :code:

Ми отримали код відповіді `201 Created`, заголовок `Location` і тіло з додатковим ідентифікатором `id`, `planID` та властивість `dateModified` - дату, що показує час, коли план закупівлі востаннє модифікувався.

Другий крок - переміщення плану в статус `scheduled`, щоб опубліковати план:

.. http:example:: tutorial/patch-plan-status-scheduled.http
   :code:

Перевіримо, що містить реєстр планів закупівель:

.. http:example:: tutorial/plan-listing.http
   :code:

Відображається  `id` - внутрішній ідентифікатор (який можна використовувати, щоб побудувати повну URL-адресу, додаючи `http://api-sandbox.openprocurement.org/api/0/plans/` на початку) та мітка часу `dateModified`.


Модифікація плану закупівлі
---------------------------

Оновимо план шляхом надання їй усіх інших важливих властивостей:

.. http:example:: tutorial/patch-plan-procuringEntity-name.http
   :code:

.. XXX body is empty for some reason (printf fails)

Ми бачимо, що додаткові властивості об’єднані з існуючими даними плану. Додатково оновлена властивість dateModified, щоб відображати останню дату модифікації.

Ще одна перевірка списку відображає нову дату модифікації:

.. http:example:: tutorial/plan-listing-after-patch.http
   :code:

.. _tender-from-plan:


Створення закупівлі з плану
---------------------------

Закупівля може бути створена з відповідного їй плану закупівлі. Закупівля буде пов’язана з планом за допомогою полів :ref:`plans тендеру <tender>` і :ref:`tender_id плану <tender_id>`.

.. note::
    | Системні збої під час створення закупівлі з плану можуть призвести до закупівель, які не пов’язані з їхніми планами по :ref:`tender_id`.
    | Переконайтеся, що ви використовуєте :ref:`2pc` і не проводте ці помилкові закупівлі (створюйте нові натомість).


Для зменшення шансів зробити помилку та зв’язати закупівлю з неправильним планом, встановлені правила валідації

.. http:example:: tutorial/tender-from-plan-validation.http
   :code:

Усього їх три:

    * procurementMethodType - відповідність типу процедури плана і тендера
    * procuringEntity.identifier - відповідність полів id і scheme для плана і тендера
    * classification.id - відповідність перших 4-х цифр кодів класифікатора плана і тендера (336 виняток - відповідність перших 3-х цифр)

План має містити джерела фінансування, інакше буде отрімано помилку під час створення тендеру:

.. http:example:: tutorial/tender-from-plan-breakdown.http
   :code:

Додамо джерело фінансування та проект до плану:

.. http:example:: tutorial/patch-plan-breakdown.http
   :code:

Успішний приклад виглядає так:

.. http:example:: tutorial/tender-from-plan.http
   :code:

Перевіримо, чи стан плану було перемкнено на `complete`:

.. http:example:: tutorial/get-complete-plan.http
   :code:

Після створення закупівлі з плану змінити план більше неможливо:

.. http:example:: tutorial/tender-from-plan-readonly.http
   :code:



Завершення плану без торгів
---------------------------

Існує спосіб завершити план без створення тендеру:

.. http:example:: tutorial/complete-plan-manually.http
   :code:

Це працює лише в тому випадку, якщо `procurementMethodType` є одним із наступних:

    * ``belowThreshold``
    * ``reporting``
    * порожній рядок


Скасування плану
----------------

План можна скасувати за допомогою :ref:`plancancellation`:

.. http:example:: tutorial/plan-cancellation.http
   :code:

Зміна статуса об’єкта скасування на ``active`` скасовує план:

.. http:example:: tutorial/plan-cancellation-activation.http
   :code:


Оновлення обгурнтування плану закупівлі
---------------------------------------

Поле ``rationale`` оновлюється у будь-якому статусі плану закупівлі:


.. http:example:: tutorial/complete-plan-rationale.http
   :code:


Історія змін полів плану закупівлі
----------------------------------

Існує окремий метод API, який дозволяє передивлятися історію полів плану закупівлі.


На даний момент підтримується тільки поле ``rationale`` :


.. http:example:: tutorial/plan-rationale-history.http
   :code:


План України
------------

Якщо зазначено джерело фінансування, Замовник може зазначати пункт Плану України в полі `budget.project`.

Якщо `project.id` вказано з довідника `plan_of_ukraine <https://prozorroukr.github.io/standards/classifiers/plan_of_ukraine.json>`_, то ми побачимо додаткові валідації на поля `name` та `name_en`:

.. http:example:: tutorial/patch-plan-budget-project-name-invalid.http
   :code:

Успішне додавання джерела фінансування разом з проектом з Плану України:

.. http:example:: tutorial/patch-plan-breakdown.http
   :code:

Ukraine facility
----------------

Для державних, місцевих бюджетів та бюджетів Автономної Республіки Крим, Замовинк має вказати код з класифікаторів Ukraine facility в полі `budget.breakdown.classification` та `budget.breakdown.address.addressDetails`.

*  Для державних бюджетів використовується класифікатор КПК. Він поділений на декілька довідників в залежності від року, наприклад `КПК-2025 <https://github.com/ProzorroUKR/standards/blob/master/classifiers/kpk_2025.json>`_.
*  Для місцевих бюджетів та бюджетів Автономної Республіки Крим використовуються класифікатори `КАТОТТГ <https://github.com/ProzorroUKR/standards/blob/master/classifiers/katottg.json>`_ та  `ТПКВКМБ <https://github.com/ProzorroUKR/standards/blob/master/classifiers/tkpkmb.json>`_

Існують додаткові валідації для планів з цими джерелами фінансування:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-state-invalid.http
   :code:

Додамо `classification` для державного бюджету:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-state.http
   :code:

Подивимося, що буде, якщо ми змінимо бюджет на місцевий:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local-invalid.http
   :code:

Додамо `classification` для місцевого бюджету і зробимо запит ще раз:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local-address-required.http
   :code:

Додамо адресу, після цього ЦБД буде вимагати КАТОТТГ для місцевого бюджету:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local-address-invalid.http
   :code:

Тепер додамо `classification` разом з `address` для місцевого бюджету:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local.http
   :code:
