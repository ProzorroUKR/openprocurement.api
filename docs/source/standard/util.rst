.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Period, startDate, endDate
.. _period:

Period
======

Schema
------

:startDate:
    string, :ref:`date`

    |ocdsDescription|
    The start date for the period.

:endDate:
    string, :ref:`date`, required 

    |ocdsDescription|
    The end date for the period.

`startDate` should always precede `endDate`.

.. _Date:

Date
====

Date/time in :ref:`date-format`.

.. index:: Value, Currency, VAT
.. _value:

Value
=====

Schema
------

:amount:
    float, required

    |ocdsDescription|
    Amount as a number.

    Should be positive.

:currency:
    string, required

    |ocdsDescription|
    The currency in 3-letter ISO 4217 format.

:valueAddedTaxIncluded:
    bool, required

.. index:: Revision, Change Tracking
.. _revision:

Revision
========

Schema
------

:date:
    string, :ref:`date`

    Date when changes were recorded.

:changes:
    List of `Change` objects

.. _guarantee:

Guarantee
=========

Schema
------

:amount:
    float, required

    |ocdsDescription|
    Amount as a number.

    Should be positive.

:currency:
    string, required, default = `UAH`

    |ocdsDescription|
    The currency in 3-letter ISO 4217 format.

.. _Change:
    
Change
======

Schema
------

:id:
    uid, auto-generated
    
    The identifier for this Change.

:rationale:
    string, multilingual, required

:dateSigned:
    string, :ref:`date`, auto-generated

:contractNumber:
    string

:status:
    string, required

    The current status of the change.

    Possible values are:

    * `pending` - this change has been added.
    * `active` - this change has been confirmed.

Workflow
--------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* marks initial state
