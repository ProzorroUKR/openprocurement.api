
.. include:: defs.hrst

.. index:: PlanCancellation

.. _plancancellation:

PlanCancellation
================

Schema
------

:id:
    uid, auto-generated

:reason:
    string, multilingual, required

    The reason, why Plan is being cancelled.

:status:
    string

    Possible values are:
     :`pending`:
       Default. The request is being prepared.
     :`active`:
       Cancellation activated.

:date:
    string, :ref:`date`

    Cancellation date.


Cancellation workflow
---------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* marks initial state


