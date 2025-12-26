
.. include:: defs.hrst

.. index:: Requirement
.. _requirement:

Requirement
===========

Схема
-----

:id:
    uid, генерується автоматично

:title:
    рядок, багатомовний, обов’язковий

    |ocdsDescription| Назва вимоги.

:status:
    рядок

    Можливі значення:

    * `active`
    * `cancelled`

    Статус вимоги (`active` за замовчуванням).

:description:
    рядок, багатомовний

    |ocdsDescription| Опис вимоги.

:dataType:
    рядок, обов'язковий

    |ocdsDescription| Визначає тип відповіді.

    Можливі значення:
     :`string`:
       Відповідь на вимогу має бути надана у строковому форматі
     :`number`:
       Відповідь на вимогу має бути надана у форматі числа
     :`integer`:
       Відповідь на вимогу має бути надана у форматі цілого числа
     :`boolean`:
       Відповідь на вимогу має бути надана у булевуму форматі

:dataSchema:
    рядок

    Визначає схему формату даних для значень з довідника. Дозволено тільки для `"dataType": "string"`

    Можливі значення:
     :`ISO 639-3`:
       Формат для `кодів мови <https://prozorroukr.github.io/standards/classifiers/languages.json>`_
     :`ISO 3166-1 alpha-2`:
       Формат для `кодів країн <https://prozorroukr.github.io/standards/classifiers/countries.json>`_

:minValue:
    int/float

    |ocdsDescription| Використовується для визначення нижньої межі вимоги, коли відповідь повинна знаходитися в певному діапазоні.

:maxValue:
    int/float

    |ocdsDescription| Використовується для визначення вищої межі вимоги, коли відповідь повинна знаходитися в певному діапазоні.

:expectedValue:
    int/float/bool

    |ocdsDescription| Використовується коли відповідь на вимогу має мати визначене значення.

:expectedValues:
    рядок

    Використовується коли відповідь на вимогу має мати визначене значення з довідника.

:period:
    :ref:`extendPeriod`

:relatedFeature:
    рядок

    Id пов'язанного :ref:`Feature`.

:eligibleEvidences:
    Список об'єктів :ref:`EligibleEvidence`.

:datePublished:
    рядок, :ref:`date`

    Дата публікації вимоги

:dateModified:
    рядок, :ref:`date`

    Дата зміни статусу вимоги на `cancelled`.