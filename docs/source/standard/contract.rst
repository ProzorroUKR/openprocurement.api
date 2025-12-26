
.. include:: defs.hrst

.. index:: Contract
.. _Contract:

Contract
========

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

    Можливі значення для :ref:`base-contracting`:

    * `active` - цей договір підписаний всіма учасниками, і зараз діє на законних підставах.
    * `terminated` - договір був підписаний та діяв, але вже завершився. Це може бути пов'язано з виконанням договору, або з достроковим припиненням через якусь незавершеність.

:period:
    :ref:`Period`

    |ocdsDescription| Дата початку та завершення договору.

:items:
    Список об’єктів :ref:`Item`, генерується автоматично, лише для читання

    |ocdsDescription| Товари, послуги та інші нематеріальні результати у цій угоді. Зверніть увагу: Якщо список співпадає з визначенням переможця `award`, то його не потрібно повторювати.

:suppliers:
    Список об’єктів :ref:`BusinessOrganization`, генерується автоматично, лише для читання

:value:
    Об’єкт :ref:`ContractValue`, генерується автоматично, лише для читання

    |ocdsDescription| Загальна вартість договору.

    Check ":ref:`SettingContractValue`" tutorial section for more info

:dateSigned:
    рядок, :ref:`date`

    |ocdsDescription| Дата підписання договору. Якщо було декілька підписань, то береться дата останнього підписання.

    Differences in :ref:`defense`, :ref:`openua` and :ref:`openeu`:

    рядок, :ref:`date`, генерується автоматично

    Діапазон значень для поля `dateSigned`:

    * для процедури звітування про укладений договір:
        [24 години назад - тепер]

    * для переговорної процедури / переговорної процедури за нагальною потребою:
        [закінчення періоду оскаржень - тепер]

:documents:
    Список об’єктів :ref:`ConfidentialDocument`

    |ocdsDescription| Усі документи та додатки пов’язані з договором, включно з будь-якими повідомленнями.


:date:
    рядок, :ref:`date`

    Дата, коли договір був змінений або активований.

    Поля немає в :ref:`base-contracting`

Додаткові поля для: :ref:`base-contracting`:


:procuringEntity:
   :ref:`ProcuringEntity`

   |ocdsDescription| Об’єкт, що управляє закупівлею. Він не обов’язково є покупцем, який платить / використовує закуплені елементи.


:changes:
    Список пов’язаних об’єктів :ref:`Change`.

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

:contractChangeRationaleTypes:
    object

    Лише для читання, генерується автоматично.

    Довідник з можливими причинами внесення змін до договору.

    Можливі значення:

        * `rationaleTypes для LAW 922 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_law_922.json>`_
        * `rationaleTypes для DECREE 1178 <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type_decree_1178.json>`_
        * `rationaleTypes general <https://github.com/ProzorroUKR/standards/blob/master/codelists/contract_change_rationale_type.json>`_ (діє до дати CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM)


Робочий процес в :ref:`base-contracting`
----------------------------------------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="terminated"]
         A -> B;
    }

\* позначає початковий стан


Contract workflow in :ref:`limited`
-----------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
         A -> B;
         A -> C;
    }

\* позначає початковий стан


Робочий процес в :ref:`openeu`
------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
         A -> B [ headlabel="Broker action"
                  labeldistance=3.7;
                  labelangle=75;
         ];
         A -> C [label="on Award cancellation"];
    }

\* позначає початковий стан


Contract in :ref:`cfaua`
========================

Схема
-----

:id:
    uid, генерується автоматично, лише для читання

:awardID:
    рядок, генерується автоматично, лише для читання

:parameters:
    Список об’єктів :ref:`Parameter` генерується автоматично, лише для читання

:suppliers:
    Список об’єктів :ref:`BusinessOrganization`, генерується автоматично, лише для читання

:status:
    рядок, обов’язковий
                   
    Можливі значення:
                 
    * `active` - participant signed the agreement
    * `unsuccessful` - participant refused to sign the agreement

:date:
    рядок, :ref:`date`

    Дата, коли договір був змінений або активований.

:bidID:
    рядок, генерується автоматично, лише для читання
                                                
    Contract related :ref:`Bid`


:unitPrices:
    List of :ref:`UnitPrice`
                        
    Contract prices per :ref:`Item`


Робочий процес в :ref:`cfaua`
-----------------------------

.. graphviz::

    digraph G {
        A [ label="active"]
        B [ label="unsuccessful"]
         A -> B;
         B -> A;
    }

\* позначає початковий стан

Contract в :ref:`frameworks_electroniccatalogue`
================================================

Схема
-----

:id:
    uid, генерується автоматично, лише для читання

:qualificationID:
    рядок, генерується автоматично, лише для читання

    ідентифікатор рішення по заявці.

:suppliers:
    Список об’єктів :ref:`BusinessOrganization`, генерується автоматично, лише для читання

:status:
    рядок, обов’язковий

    Можливі значення:

    * `active`
    * `banned`
    * `unsuccessful`
    * `terminated`

:milestones:
      Список об’єктів :ref:`Milestone`.

:date:
    рядок, :ref:`date`

    Дата, коли договір був змінений або активований.

