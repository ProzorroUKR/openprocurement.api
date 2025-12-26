
.. include:: defs.hrst

.. index:: Cancellation
.. _cancellation:

Cancellation
============

Схема
-----

:id:
    uid, генерується автоматично

:reason:
    рядок, багатомовний, обов’язковий

    Причина, з якої скасовується закупівля.

:status:
    рядок

    Можливі значення:
     :`draft`:
       За замовчуванням. Скасування у стані формування.
     :`pending`:
       Запит оформлюється.
     :`active`:
       Скасування активоване.
     :`unsuccessful`:
       Невдале скасування

:documents:
    Список об’єктів :ref:`ConfidentialDocument`

    Супровідна документація скасування: Протокол рішення Тендерного комітету Замовника про скасування закупівлі.

:date:
    рядок, :ref:`date`

    Дата скасування

:cancellationOf:
    string, обов’язковий, за замовчуванням `tender`

    Можливі значення:

    * `tender` - закупівля
    * `lot` - лот

    Можливі значення у :ref:`limited`: * `tender`

:relatedLot:
    рядок

    ID пов’язаного :ref:`lot`.

:reasonType:
    рядок

    Існує чотири можливi причини скасування для процедур `reporting`, `aboveThreshold`, `aboveThresholdUA`, `aboveThresholdEU`, `esco`, `competitiveDialogueEU`, `competitiveDialogueUA`, `competitiveDialogueEU.stage2`, `competitiveDialogueUA.stage2`, `closeFrameworkAgreementUA`, `closeFrameworkAgreementSelectionUA`, `competitiveOrdering`, `priceQuotation`:

     :`noDemand`:
       Відсутність подальшої потреби в закупівлі товарів, робіт і послуг.

     :`unFixable`:
       Неможливість усунення виявлених порушень законодавства у сфері публічних закупівель.

     :`forceMajeure`:
       Неможливість здійснення закупівлі унаслідок непереборної сили.

     :`expensesCut`:
       Скорочення видатків на здійснення закупівлі товарів, робіт і послуг.


    Ще одна можлива причина скасування для процедур `aboveThreshold` і `competitiveOrdering`:

     :`noOffer`:
       Подано менше 2 тендерних пропозицій.

    Можливі причини скасування для `negotiation` та `negotiation.quick`:

     :`noDemand`:
       Відсутність подальшої потреби в закупівлі товарів, робіт і послуг.

     :`unFixable`:
       Неможливість усунення виявлених порушень законодавства у сфері публічних закупівель.

     :`noObjectiveness`:
       Неможливість здійснення закупівлі унаслідок непереборної сили.

     :`expensesCut`:
       Скорочення видатків на здійснення закупівлі товарів, робіт і послуг.

     :`dateViolation`:
       Скорочення видатків на здійснення закупівлі товарів, робіт і послуг.

    Моживі причини скасування для `aboveThresholdUA.defense` та `aboveThresholdUA.defense`:

     :`noDemand`:
       Відсутність подальшої потреби в закупівлі товарів, робіт і послуг.

     :`unFixable`:
       Неможливість усунення виявлених порушень законодавства у сфері публічних закупівель.

     :`expensesCut`:
       Скорочення видатків на здійснення закупівлі товарів, робіт і послуг.

:complaintPeriod:
    :ref:`period`

    Період, під час якого можна подавати скарги.

:complaints:
    Список об’єктів :ref:`complaint`


Робочий процес у :ref:`limited` and :ref:`openeu`
-------------------------------------------------

.. graphviz::

    digraph G {
        A [ label="draft*" ]
        B [ label="pending" ]
        C [ label="active"]
        D [ label="unsuccessful" ]
        A -> {B,D};
        B -> {C,D};
    }

\* позначає початковий стан


