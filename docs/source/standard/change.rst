
.. include:: defs.hrst


.. _ChangeTaxRate:

ChangeTaxRate in :ref:`cfaua`
=============================

Схема
-----

.. include:: base_change.rst

:rationaleType:
    рядок

     Значення за замовчуванням - `taxRate`.

:modifications:
    Список об'єктів :ref:`UnitPriceModification`

     * Для `UnitPriceModification` в `ChangeTaxRate` дозволяється тільки один атрибут (`factor` або `addend` ).


.. _ChangeItemPriceVariation:

ChangeItemPriceVariation in :ref:`cfaua`
========================================

Схема
-----

.. include:: base_change.rst

:rationaleType:
    рядок

     Значення за замовчуванням - `itemPriceVariation`.

:modifications:
    Список об'єктів :ref:`UnitPriceModification`

     * Для `UnitPriceModification` в `ChangeItemPriceVariation` дозволяється тільки атрибут `factor`. Атрибут `factor` має бути в межах 0.9 - 1.1.


.. _ChangeThirdParty:

ChangeThirdParty in :ref:`cfaua`
================================

.. include:: base_change.rst

:rationaleType:
    рядок

     Значення за замовчуванням - `thirdParty`.

:modifications:
    Список об'єктів :ref:`UnitPriceModification`

     * Для `UnitPriceModification` в `ChangeThirdParty` дозволяється тільки атрибут `factor`. Атрибут `factor` має бути більше 0.0.


.. _ChangePartyWithdrawal:

ChangePartyWithdrawal in :ref:`cfaua`
=====================================

Схема
-----

.. include:: base_change.rst

:rationaleType:
    рядок

     Значення за замовчуванням - `partyWithdrawal`.

:modifications:
    Список об'єктів :ref:`ContractModification`


.. _UnitPriceModification:

UnitPriceModification in :ref:`cfaua`
=====================================

Схема
-----

:itemId:
    рядок

     Ідентифікатор змінюваного об'єкту.

:factor:
    неціле число

     Мінімальне значення - 0.0.

:addend:
    неціле число

     Абсолютне значення зміни. Примітка: `factor` і `addend` не є обов'язковими полями, але хоча б одне поле має бути заповненим.


.. _ContractModification:

ContractModification in :ref:`cfaua`
====================================

Схема
-----

:itemId:
    рядок

     Ідентифікатор змінюваного об'єкту.

:contractId:
    рядок, обов'язковий


Схема роботи
------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* позначає початковий стан


