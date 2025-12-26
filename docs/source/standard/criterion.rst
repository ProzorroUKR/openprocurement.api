
.. include:: defs.hrst

.. index:: Criterion
.. _criterion:

Criterion
=========

Схема
-----

:id:
    uid, генерується автоматично

:title:
    рядок, багатомовний, обов’язковий

    |ocdsDescription| Назва критерію.

:description:
    рядок, багатомовний

    |ocdsDescription| Опис критерію.

:source:
    рядок

    |ocdsDescription| Джерело відповіді на вимоги, зазначені в критерії. Наприклад, відповіді можуть бути подані учасниками тендеру або замовником.

    Можливі значення:
     :`tenderer`:
       Відповідь надається учасником.
     :`buyer`:
       Відповідь надається замовником.
     :`procuringEntity`:
       Відповідь надається закупівельником.
     :`ssrBot`:
       Відповідь надається ботом.
     :`winner`:
       Відповідь надається переможцем.

:relatesTo:
    рядок

    |ocdsDescription| Елемент схеми, який критерій оцінює. Наприклад, критерій може бути визначений щодо позицій або проти учасників торгів.

    Можливі значення:
     :`tenderer`:
       Критерій відноситься до учасника.
     :`item`:
       Критерій відноситься до предмету.
     :`lot`:
       Критерій відноситься до лоту.

:relatedItem:
    рядок

    :якщо relatesTo == tender:
      Поле повинно бути пустим.
    :якщо relatesTo == item:
      Id пов'язаного :ref:`item`
    :якщо relatesTo == lot:
      Id пов'язаного :ref:`lot`

:classification:
    :ref:`Classification`

    |ocdsDescription| Основна класифікація елемента

:additionalClassifications:
    Список об'єктів :ref:`Classification`.

    |ocdsDescription| Масив додаткових класифікацій елемента.

:legislation:
    Список об'єктів :ref:`LegislationItem`.

:requirementGroups:
    Список об'єктів :ref:`RequirementGroup`.
