
.. include:: defs.hrst

.. index:: Period, startDate, endDate
.. _period:

Period
======

Схема
-----

:startDate:
    рядок, :ref:`date`

    |ocdsDescription| Початкова дата періоду.

:endDate:
    рядок, :ref:`date`

    |ocdsDescription| Кінцева дата періоду.

Значення `startDate` завжди повинно йти перед `endDate`.


.. _ExtendPeriod:

ExtendPeriod
============

Схема
-----

:startDate:
    рядок, :ref:`date`

    |ocdsDescription| Початкова дата періоду.

:endDate:
    рядок, :ref:`date`

    |ocdsDescription| Кінцева дата періоду.

:maxExtendDate:
    рядок, :ref:`date`

    |ocdsDescription| Період не можна продовжувати після цієї дати.

:durationInDays:
    integer

    |ocdsDescription| Максимальна тривалість цього періоду в днях. Якщо вказані дата початку та закінчення, це поле є необов’язковим і повинно відображати різницю між цими двома днями.

:duration:
    рядок, :ref:`date`

    |ocdsDescription| Тривалість періоду відображена у форматі ISO.

Значення `startDate` завжди повинно йти перед `endDate`.


.. _Date:

Date
====

Дата/час у :ref:`date-format`.

.. index:: ContractValue, Value, Currency, VAT
.. _ContractValue:

ContractValue
=============

Схема
-----

:amount:
    float, обов’язково

    |ocdsDescription| Кількість як число.

    Повинно бути додатнім.

:amountNet:
    float

    |ocdsDescription| Кількість як число.

    Повинно бути додатнім.

:currency:
    рядок, обов’язковий

    |ocdsDescription| Валюта у трибуквенному форматі ISO 4217.

:valueAddedTaxIncluded:
    bool, обов’язково

.. index:: Value, Currency, VAT
.. _value:

Value
=====

Схема
-----

:amount:
    float, обов’язково

    |ocdsDescription| Кількість як число.

    Повинно бути додатнім.

    Відсутня в :ref:`esco`

:currency:
    рядок, обов’язковий

    |ocdsDescription| Валюта у трибуквенному форматі ISO 4217.

:valueAddedTaxIncluded:
    bool, обов’язково

Додатково у :ref:`esco`:

:annualCostsReduction:
    21-елементний список float, обов’язковий.

    Buyer’s annual costs reduction. A 21-element array where the 1st element indicates cost reduction starting from the period of tender notice publication date till the end of the year. Value can be changed only during active tendering period (active.tendering).

:yearlyPaymentsPercentage:
    float, обов’язково

    The percentage of annual payments in favor of Bidder.

    Можливі значення:

    * from 0.8 to 1 (from 80% to 100% respectively) if fundingKind:other.
    * from 0 to x, where x can vary from 0 to 0.8 (from 0% to x% respectively) if fundingKind:budget.

    Input precision - 3 digits after comma.

:amountPerformance:
    float, генерується автоматично

    Calculated energy service contract performance indicator. Calculated by the energy service contract performance indicator energy service contract performance indicator formula.

:amount:
    float, генерується автоматично

    Calculated energy service contract value. Calculated by the energy service contract value formula.

:contractDuration:

    :ref:`ContractDuration <contact_duration>`, required.


.. _contact_duration:

ContractDuration
================

Схема
-----

:years: integer, обов’язковий

    Можливі значення: 0-15

:days:  integer, не обов’язковий

    Можливі значення: 0-364

    Default value: 0

.. index:: Revision, Change Tracking
.. _revision:

Revision
========

Схема
-----

:date:
    рядок, :ref:`date`

    Дата, коли зміни були записані.

:changes:
    Список об’єктів `Change`


.. _BasicValue:

BasicValue
==========

Схема
-----

:amount:
    float, обов’язково

    |ocdsDescription| Кількість як число.

    Повинно бути додатнім.

:currency:
    рядок, обов’язковий, за замовчуванням = `UAH`

    |ocdsDescription| Валюта у трибуквенному форматі ISO 4217.


.. _BankAccount:

BankAccount
===========

Схема
-----

:id:
    рядок, обов’язковий

    Унікальний ідентифікатор для BankAccount.

:scheme:
    рядок, обов’язковий

    Можливі значення:

     * `IBAN` - International Bank Account Number

.. _OrganizationReference:

OrganizationReference
=====================

Схема
-----


:bankAccount:
    рядок, :ref:`BankAccount`, обов’язковий

:name:
    рядок, обов’язковий

    Поле імені, яке повторює ім'я, вказане в розділі сторін, передбачене для зручності перегляду даних і для підтримки виявлення помилок при перехресних посиланнях.


.. _Reference:

Reference
=========

Схема
-----

:id:
    рядок, обов’язковий

    Ідентифікатор, що використовується для перехресного посилання на запис у розділі сторін, який містить повну інформацію про цю організацію чи сутність.

:title:
    рядок, обов’язковий

    Поле імені, яке повторює ім'я, вказане в розділі сторін, передбачене для зручності перегляду даних і для підтримки виявлення помилок при перехресних посиланнях.


.. _LegislationItem:

LegislationItem
===============

Схема
-----

:version:
    рядок

:identifier:
    :ref:`Identifier`

:type:
    рядок

    Можливі значення:
     * `NATIONAL_LEGISLATION`

:article:
    рядок



.. _Change:

Change
======

Схема
-----

:id:
    uid, генерується автоматично

    Ідентифікатор для цієї зміни.

:rationale:
    рядок, багатомовний, обов’язковий

    Причина зміни контракту

:rationaleTypes:
    Список рядків, обов’язковий

    Тип причини додання змін до договору

    Можливі значення валідуються зі списку причин, вказаних в полі `contractChangeRationaleTypes`. Можуть бути одні з:

        * `rationaleTypes для LAW 922 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_law_922.json>`_
        * `rationaleTypes для DECREE 1178 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_decree_1178.json>`_
        * `rationaleTypes general <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type.json>`_ (діє до дати CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM)

:date:
    рядок, :ref:`date`, генерується автоматично

:dateSigned:
    рядок, :ref:`date`

:contractNumber:
    рядок

:status:
    рядок, обов’язковий

    Поточний стан зміни.

    Можливі значення:

    * `очікування` - ця зміна була додана.

    * `активний` - ця зміна підтверджена.

Робочий процес
--------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* позначає початковий стан


.. _CauseDetails:

CauseDetails
============

Схема
-----

:code:
    рядок, обов’язковий для **переговорної** процедури та **переговорної процедури за нагальною потребою**. Також обов’язковий для **звітів**, які мають пусте поле `procurementMethodRationale`, в полі `procuringEntity.kind` вказано щось відмінне від `other` та очікувана вартість перевищує поріг:

        * 100 000 для товарів,
        * 200 000 для послуг,
        * 1 500 000 для робіт.

    Обгрунтування використання звітів, \”звичайної\” переговорної процедури або переговорної процедури за нагальною потребою.

    Можливі значення зберігаються у довідниках в залежності від `procurementMethodType`:

        * `reporting <https://github.com/ProzorroUKR/standards/blob/master/codelists/tender/tender_cause_details/reporting.json>`_
        * `negotiation <https://github.com/ProzorroUKR/standards/blob/master/codelists/tender/tender_cause_details/negotiation.json>`_
        * `negotiation.quick <https://github.com/ProzorroUKR/standards/blob/master/codelists/tender/tender_cause_details/negotiation.quick.json>`_

:scheme:
    рядок

    Схема обгрунтування (закон/постанова), з якого буде вказана підстава. Автоматично заповнюється на ЦБД значенням з довідника. Можливі значення:

    * `LAW922`
    * `DECREE1178`

:title:
    рядок, багатомовний

    Юридичне обгрунтування використання звітів, \”звичайної\” переговорної процедури або переговорної процедури за нагальною потребою. Автоматично заповнюється на ЦБД значенням з довідника.


:description:
    рядок, багатомовний

    Обгрунтування використання звітів, \”звичайної\” переговорної процедури або переговорної процедури за нагальною потребою.
