
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
    string, required, default `tender`

    Possible values are:

    * `tender`
    * `lot`

    Possible values in :ref:`limited`:
    * `tender`

:relatedLot:
    string

    Id of related :ref:`lot`.


Additionally in :ref:`openeu`, :ref:`openua` and :ref:`esco`:

:reasonType:
    string

    There are two possible types of cancellation reason set by procuring entity:

     :`cancelled`:
       Default. Tender was cancelled.

     :`unsuccessful`:
       Tender was unsuccessful.

Cancellation workflow in :ref:`limited` and :ref:`openeu`
---------------------------------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* marks initial state


