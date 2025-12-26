
.. include:: defs.hrst


.. _EContractChange:

EContractChange
===============

Схема
-----

:id:
    uid, генерується автоматично

    Ідентифікатор для об'єкта Change

:rationale:
    рядок, багатомовний, обов'язковий

    Причина для зміни договору

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

    |ocdsDescription| Дата підписання додаткової угоди. Якщо було декілька підписань, то береться дата останнього підписання.

:status:
    рядок, обов’язковий

    Поточний стан зміни.

    Можливі значення:

    * `очікування` - ця зміна була додана.

    * `активний` - ця зміна підтверджена.

    * `cancelled` - ця зміна скасована.

:modifications:
    Список об'єктів :ref:`EContractModifications`

    Поля договору, які будуть змінені, якщо ченжи будуть підписані.

:documents:
    Список об’єктів :ref:`ConfidentialDocument`

    Всі документи (підписи), які пов'язані із скасуванням.

:cancellations:
   Список пов’язаних об’єктів :ref:`EContractCancellation`.

   Містить 1 об’єкт зі статусом `active` на випадок, якщо ченж буде відмінено

   Об’єкт :ref:`EContractCancellation` описує причину скасування ченжів.

:author:
    рядок, генерується автоматично

    Автор ченжів

.. _EContractModifications:

ContractModifications
=====================

Схема
-----

:title:
    рядок, обов’язковий

    |ocdsDescription| Назва договору

:description:
    рядок

    |ocdsDescription| Опис договору

:period:
    :ref:`Period`

    |ocdsDescription| Дата початку та завершення договору.

:value:
    Об’єкт :ref:`ContractValue`, генерується автоматично, лише для читання

    |ocdsDescription| Загальна вартість договору.

    Check ":ref:`SettingContractValue`" tutorial section for more info

:items:
    Список об’єктів :ref:`Item`, генерується автоматично, лише для читання

    |ocdsDescription| Товари, послуги та інші нематеріальні результати у цій угоді. Зверніть увагу: Якщо список співпадає з визначенням переможця `award`, то його не потрібно повторювати.

:contractNumber:
    рядок
