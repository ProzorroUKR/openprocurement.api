
.. include:: defs.hrst

.. index:: Award
.. _award:

Award
=====

Схема
-----

:id:
    рядок, генерується автоматично, лише для читання
                                                
    |ocdsDescription| Ідентифікатор цього рішення.
                                              
:bid_id:
    рядок, генерується автоматично, лише для читання

    ID пропозиції, що виграла закупівлю.

    відсутній у :ref:`limited`:
                           
:title:
    рядок, багатомовний
                   
    |ocdsDescription| Назва рішення.
                                
:description:
    рядок, багатомовний
                   
    |ocdsDescription| Опис рішення.
                               
:status:
    рядок
     
    |ocdsDescription| Поточний статус рішення, взятий зі списку кодів `awardStatus`.

    Можливі значення:

    * `pending` - переможець розглядається кваліфікаційною комісією
    * `unsuccessful` - кваліфікаційна комісія відмовила переможцю
    * `active` - закупівлю виграв учасник з пропозицією `bid_id`
    * `cancelled` - орган, що розглядає скарги, відмінив результати закупівлі

:date:
    рядок, :ref:`Date`, генерується автоматично, лише для читання
                                                             
    |ocdsDescription| Дата рішення про підписання договору.
                                                       
:value:
    Об’єкт :ref:`Value`, генерується автоматично, лише для читання

    |ocdsDescription| Загальна вартість згідно цього рішення.

    Відмінності :ref:`defense`, :ref:`esco`, :ref:`openua` та :ref:`openeu`:

    Список :ref:`Value` об’єктів, генерується автоматично, лише для читання

    Відмінності у :ref:`limited`:

    Об'єкт `Value`

:suppliers:
    Список об’єктів :ref:`BusinessOrganization`, генерується автоматично, лише для читання
                                                                                      
    |ocdsDescription| Постачальники, що були визнані переможцями згідно цього рішення.
                                                                                  
:items:
    Список об’єктів :ref:`Item`, генерується автоматично, лише для читання
                                                                      
    |ocdsDescription| Товари та послуги, що розглядались цим рішенням, поділені на окремі рядки, де це можливо. Елементи не повинні бути продубльовані, а повинні мати вказану кількість. 
    
:documents:
    Список об’єктів :ref:`ConfidentialDocument`
                                           
    |ocdsDescription| Усі документи та додатки пов’язані з рішенням, включно з будь-якими повідомленнями. 
    
:complaints:
    |    Список об’єктів :ref:`Complaint` та :ref:`Claim`.

    |    Список об’єктів :ref:`Claim` для `belowThreshold`.
    |    Список об’єктів :ref:`Complaint` для `negotiation` and `negotiation.quick`.


:complaintPeriod:
    :ref:`period`

    Період, під час якого можна подавати скарги.

:lotID:
    рядок

    ID пов’язаного :ref:`lot`.

    Відмінності у :ref:`limited`:

        Id пов'язаного :ref:`lot`. Тільки для процуде з `tender.procurementMethodType`: `negotiation` чи `negotiation.quick`.

:qualified:
    bool

    Підтверджує відсутність підстав для відмови від участі відповідно до статті 17 Закону України ”Про державні закупівлі”.


Відмінності :ref:`defense`, :ref:`esco`, :ref:`competitivedialogue`, :ref:`cfaua`, :ref:`open`, :ref:`openua` та :ref:`openeu`:

:eligible:
    bool

    Підтверджує відповідність критеріям прийнятності, встановлених замовником в тендерній документації.

Додатково для всіх процедур окрім :ref:`limited`:

:period:
    :ref:`Period`

    Період для прийняття рішення по аварду.


Додатково :ref:`limited`:

:subcontractingDetails:
    рядок

    Текстове поле будь-якої довжини, що містить інформацію про субпідрядника.

:requirementResponses:
        Список об’єктів :ref:`RequirementResponse`.

Робочий процес нагороди в :ref:`limited`:
-----------------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
         A -> B;
         A -> D;
         B -> C;
    }

\* marks initial state


Робочий процес у :ref:`openeu` та :ref:`esco`:
----------------------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
         A -> B;
         A -> D;
         B -> C;
         D -> C;
    }

\* marks initial state
