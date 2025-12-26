.. include:: defs.hrst
.. index:: Plan, PlanOrganization, PlanTender, Budget, Project, BudgetPeriod
.. _plan:

Plan
====

planID
------
   рядок, генерується автоматично, лише для читання

   Ідентифікатор плану для позначення плану в "паперовій" документації.

   |ocdsDescription| Ідентифікатор тендера `TenderID` повинен завжди співпадати з OCID. Його включають, щоб зробити структуру даних більш зручною.

procuringEntity
---------------

   :ref:`PlanOrganization`, обов’язково

   Замовник (організація, що проводить закупівлю).

   |ocdsDescription| Об’єкт, що управляє закупівлею. Він не обов’язково є покупцем, який платить / використовує закуплені елементи.

status
------

   рядок

   Можливі значення:
        * draft
        * scheduled
        * cancelled
        * complete

   Статус плану.

   .. graphviz::

        digraph G {

            rankdir = LR

            draft [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = cadetblue1
            ]
            scheduled [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = deepskyblue1
            ]
            complete [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = aquamarine3
            ]
            cancelled [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = coral1
            ]

            draft -> scheduled
            scheduled -> complete
            scheduled -> cancelled
        }

buyers
------
   Cписок об’єктів :ref:`PlanOrganization`, обов’язково 1 об’єкт

   Cуб’єкт(и) в інтересах якого(их) проводиться закупівля

   Validation depends on:

        * :ref:`PLAN_BUYERS_REQUIRED_FROM` constant


milestones
----------

   Список об’єктів :ref:`PlanMilestone`

   Майлстоуни типу “затвердження” використовуються для того, щоб надати центральній організації закупівель функцію затвердження

   Validation depends on:

        * :ref:`MILESTONES_VALIDATION_FROM` constant

tender
------
   :ref:`PlanTender`, обов’язково

   Дані щодо тендерного процесу.

budget
------
   :ref:`Budget`, обов’язково (за вийнятком `tender.procurementMethodType` має значення `"esco"`)

   Повний доступний бюджет закупівлі.

   |ocdsDescription| Загальна кошторисна вартість закупівлі.


project
-------
   :ref:`Project`

   |ocdsDescription| Об’єкт проекту, який описує інфраструктуру або проект державно-приватного партнерства, з яким пов’язаний процес планування.



classification
--------------

    :ref:`Classification`, обов’язково

    |ocdsDescription| Початкова класифікація елемента. Дивіться у itemClassificationScheme, щоб визначити бажані списки класифікації, включно з CPV та GSIN.

    Класифікація `classification.scheme` обов’язково повинна бути `CPV` або `ДК021`. `classification.id` повинно бути дійсним CPV або ДК021 кодом.

additionalClassifications
-------------------------

    Список об’єктів :ref:`Classification`

    |ocdsDescription| Масив додаткових класифікацій для елемента. Дивіться у список кодів itemClassificationScheme, щоб використати поширені варіанти в OCDS. Також можна використовувати для представлення кодів з внутрішньої схеми класифікації.

    Елемент, у якому classification.id починається з 336 і містить додаткові об’єкти класифікації, повинен містити не більше однієї додаткової класифікації зі схемою INN.

    Елемент з classification.id = 33600000-6 повинен містити рівно одну додаткову класифікацію зі схемою = INN.

    Обов’язково мати принаймні один елемент з `ДКПП` як `scheme`.

documents
---------
   Список об’єктів :ref:`document`

   |ocdsDescription| Всі документи та додатки пов’язані із закупівлею.

.. _tender_id:

tender_id
---------

   рядок, генерується автоматично, лише для читання

   ``id`` пов’язаного тендер об’єкта. Див :ref:`tender-from-plan`

items
-----
   список об’єктів :ref:`item`, обов’язково

   Список, який містить елемент, що закуповується.

   |ocdsDescription| Товари та послуги, що будуть закуплені, поділені на спискові елементи, де це можливо. Елементи не повинні дублюватись, замість цього вкажіть кількість 2.

cancellation
------------

    :ref:`PlanCancellation`

milestones
----------
   Список об’єктів :ref:`PlanMilestone`

dateModified
------------
   рядок, :ref:`date`, генерується автоматично

datePublished
-------------
   рядок, :ref:`date`, генерується автоматично

owner
-----
    рядок, генерується автоматично

revisions
---------
   Список об’єктів :ref:`revision`, генерується автоматично, лише для читання

   Зміни властивостей об’єктів Закупівлі.


-----------


.. _PlanTender:

PlanTender
==========


procurementMethod
-----------------
    рядок

    Можливі значення:
                 
        * 'open'
        * 'limited'

    Метод закупівлі тендеру.


procurementMethodType
---------------------
    можливі значення для `procurementMethod` == `''`:

    * '' - Без використання електронної системи
    * 'centralizedProcurement' - Закупівля через Централізовану закупівельну організацію

    Можливі значення для `procurementMethod` == `’open’`:

    * belowThreshold
    * aboveThresholdUA
    * aboveThresholdEU
    * aboveThresholdUA.defense
    * esco
    * closeFrameworkAgreementUA
    * competitiveDialogueEU
    * competitiveDialogueUA

    Можливі значення для `procurementMethod` == `’limited’`:

    * reporting
    * negotiation
    * negotiation.quick


tenderPeriod
------------
   :ref:`period`, обов’язково

   Період, коли подаються пропозиції. Повинна бути вказана хоча б `endDate` дата.

   |ocdsDescription| Період, коли закупівля відкрита для подачі пропозицій. Кінцева дата - це дата, коли перестають прийматись пропозиції.

-----------

.. _Project:

Project
=======

id
--
    рядок

title
-----
    рядок, обов’язковий

uri
---
    рядок, обов’язковий

-----------

.. _Budget:

Budget
======

id
--
    рядок, обов’язковий

description
-----------
    рядок, багатомовний, обов’язковий

amount
------
    float, обов’язково

amountNet
---------
    float, обов’язково

currency
--------
    рядок, обов’язковий, довжина = 3

project
-------
    :ref:`BudgetProject`

period
------
    :ref:`BudgetPeriod`

    Validation depends on:

        * :ref:`BUDGET_PERIOD_FROM` constant

year
----
    integer, >=2000, deprecated in favor of `period`_

    Validation depends on:

        * :ref:`BUDGET_PERIOD_FROM` constant

notes
-----
    рядок

breakdown
---------
    Список об’єктів :ref:`BudgetBreakdown`, обов’язковий (за вийнятком `tender.procurementMethodType` має значення `"belowThreshold"`, `"reporting"`, `"esco"`, `""`)


-----------


.. _BudgetProject:

BudgetProject:
==============

id
--
    рядок, обов’язковий

name
----
    рядок, обов’язковий

name_en
-------
    рядок

-----------

.. _BudgetPeriod:

BudgetPeriod
============

startDate
---------
    рядок, обов’язковий, :ref:`date`

    |ocdsDescription| Початкова дата періоду.

endDate
-------
    рядок, обов’язковий, :ref:`date`

    |ocdsDescription| Кінцева дата періоду.

Значення `startDate` завжди повинно йти перед `endDate`.

.. _BudgetBreakdown:

BudgetBreakdown
===============

:id:
    uid, генерується автоматично

:title:
    рядок, обов’язковий

    Можливі значення:

    * `state`
    * `crimea`
    * `local`
    * `own`
    * `fund`
    * `loan`
    * `other`

:description:
    рядок, багатомовний, обов’язковий за умови title == `other`

    Детальний опис джерел фінансування закупівлі.

:value:
    :ref:`BasicValue`

    Cума, яка виділена для окремого джерела фінансування

    Валюта для всіх breakdown value та budget повинна бути однаковою

    Загальна вартість всіх breakdown value amount не може бути більшим за budget amount (за вийнятком `tender.procurementMethodType` має значення `"esco"`)

:address:
    :ref:`Address`

    Об'єкт з деталями адреси джерела фінансуванння `budget.breakdown`.

    Якщо джерело фінансування `budget.breakdown.title` вказано `state`, класифікатор КАТОТТГ має зазначатись обовʼязково.


:classification:

    Список об’єктів :ref:`Classification`

    Класифікатор для бюджету в залежності від джерела фінансуванння `budget.breakdown`.

    Якщо джерело фінансування `budget.breakdown.title` вказано одне зі значень `local`, `crimea`, класифікатор ТПКВКМБ має зазначатись обовʼязково.

    Якщо джерело фінансування `budget.breakdown.title` вказано `state`, класифікатор КПК має зазначатись обовʼязково.
