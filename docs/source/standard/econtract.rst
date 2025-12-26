
.. include:: defs.hrst

.. index:: EContract
.. _EContract:

EContract
=========

Схема
-----

:id:
    uid, генерується автоматично

    |ocdsDescription| Ідентифікатор цього договору.

:awardID:
    рядок, обов’язковий

    |ocdsDescription| `Award.id` вказує на рішення, згідно якого видається договір.

:contractID:
    рядок, генерується автоматично, лише для читання

:contractNumber:
    рядок

:title:
    рядок, обов’язковий

    |ocdsDescription| Назва договору

:description:
    рядок

    |ocdsDescription| Опис договору

:status:
    рядок, обов’язковий

    |ocdsDescription| Поточний статус договору.

    Можливі значення:

    * `pending` - цей договір запропоновано, але він ще не діє. Можливо очікується його підписання.
    * `active` - цей договір підписаний всіма учасниками, і зараз діє на законних підставах.
    * `cancelled` - цей договір було скасовано до підписання.

    * `terminated` - договір був підписаний та діяв, але вже завершився. Це може бути пов'язано з виконанням договору, або з достроковим припиненням через якусь незавершеність.

:period:
    :ref:`Period`

    |ocdsDescription| Дата початку та завершення договору.

:items:
    Список об’єктів :ref:`Item`, генерується автоматично, лише для читання

    |ocdsDescription| Товари, послуги та інші нематеріальні результати у цій угоді. Зверніть увагу: Якщо список співпадає з визначенням переможця `award`, то його не потрібно повторювати.

:suppliers:
    Список об’єктів :ref:`EContractOrganization`, генерується автоматично, лише для читання

:value:
    Об’єкт :ref:`ContractValue`, генерується автоматично, лише для читання

    |ocdsDescription| Загальна вартість договору.

    Check ":ref:`SettingContractValue`" tutorial section for more info

:dateSigned:
    рядок, :ref:`date`

    |ocdsDescription| Дата підписання договору. Якщо було декілька підписань, то береться дата останнього підписання.


:documents:
    Список об’єктів :ref:`ConfidentialDocument`

    |ocdsDescription| Усі документи та додатки пов’язані з договором, включно з будь-якими повідомленнями.


:buyer:
   :ref:`EContractOrganization`

   |ocdsDescription| Об’єкт, що управляє закупівлею. Він не обов’язково є покупцем, який платить / використовує закуплені елементи.


:changes:
    Список пов’язаних об’єктів :ref:`EContractChange`.

:amountPaid:

    :amount: число з рухомою комою, обов’язкове
    :currency: рядок, обов’язковий, генерується автоматично
    :valueAddedTaxIncluded: логічний (булевий) тип даних, обов’язковий, генерується автоматично

    Дійсно оплачена сума.

:implementation:
    :ref:`Implementation`

:terminationDetails:
    рядок, обов’язковий для неуспішних договорів

    Причина припинення договору. Наявність цього поля вказує, що договір є неуспішним.

:contractTemplateName:
    рядок, генерується автоматично

    посилання на шаблон а стандртах

:cancellations:
   Список пов’язаних об’єктів :ref:`EContractCancellation`.

   Містить 1 об’єкт зі статусом `active` на випадок, якщо версію договора буде відмінено.

   Об’єкт :ref:`EContractCancellation` описує причину скасування договору та надає відповідні документи, якщо такі є..

:author:
    рядок, генерується автоматично

    Автор нової версії договору (якщо попередня версія була скасована)

:contractChangeRationaleTypes:
    object

    Лише для читання, генерується автоматично.

    Довідник з можливими причинами внесення змін до договору.

    Можливі значення:

        * `rationaleTypes для LAW 922 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_law_922.json>`_
        * `rationaleTypes для DECREE 1178 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_decree_1178.json>`_
        * `rationaleTypes general <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type.json>`_ (діє до дати CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM)


Робочий процес
--------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active" ]
        C [ label="cancelled" ]
        D [ label="terminated"]
         A -> B;
         A -> C [label="on Award cancellation or contract set status"] ;
         B -> D;
    }

\* позначає початковий стан
