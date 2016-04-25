.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Cancellation
.. _cancellation:

Cancellation
============

Schema
------

:id:
    uid, auto-generated

:reason:
    string, multilingual, required

    The reason, why Tender is being cancelled.

:status:
    string

    Possible values are:
     :`pending`:
       Default. The request is being prepared.
     :`active`:
       Cancellation activated.

:documents:
    List of :ref:`Document` objects

    Documents accompanying the Cancellation: Protocol of Tender Committee
    with decision to cancel the Tender.

:date:
    string, :ref:`date`

    Cancellation date.

:cancellationOf:
    string, required 

    Possible and default values are:

    * `tender`

:relatedLot:
    string

    Id of related :ref:`lot`.

Cancellation workflow
---------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* marks initial state
