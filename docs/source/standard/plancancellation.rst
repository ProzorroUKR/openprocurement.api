
.. include:: defs.hrst

.. index:: PlanCancellation

.. _plancancellation:

PlanCancellation
================

Schema
------

:id:
    uid, генерується автоматично

:reason:
    рядок, багатомовний, обов’язковий

    Причина, з якої скасовується план.

:status:
    string

    Можливі значення:
     :`pending`:
       За замовчуванням. Запит оформляється.
     :`active`:
       Скасування активоване.

:date:
    рядок, :ref:`date`

    Дата скасування.


Робочий процес
--------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* позначає початковий стан


