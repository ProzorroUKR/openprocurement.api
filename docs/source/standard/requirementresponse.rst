
.. include:: defs.hrst

.. index:: RequirementResponse
.. _RequirementResponse:

RequirementResponse
===================

Схема
-----

:id:
    uid, генерується автоматично

:title:
    рядок, багатомовний, обов’язковий

    |ocdsDescription| Назва відповіді на вимогу.

:description:
    рядок, багатомовний

    |ocdsDescription| Опис відповіді на вимогу.

:period:
    :ref:`extendPeriod`

:requirement:
    :ref:`Reference`

    |ocdsDescription| Посилання на вимогу.

:relatedTenderer:
     :ref:`Reference`

    |ocdsDescription| Посилання на організацію.

:relatedItem:
    string

    Id пов'язанного об'єкту :ref:`item`.

:evidences:
    Список об'єктів :ref:`Evidence`

:values:
    Список рядків

    Значення мають бути зі списку `requirement.expectedValues`. Це поле необхідно передавати у випадку, коли характеристика має `dataType: string`.

:value:
    boolean/int/decimal

    Значення відповіді на цю вимогу. Значення має бути типом, визначеним у полі requirement.dataType. Це поле необхідно передавати у випадку, коли характеристика має будь-який `dataType`, окрім `string`.
