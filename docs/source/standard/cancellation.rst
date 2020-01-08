
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
     :`draft`:
       Default. Cancellation in a state of formation.
     :`pending`:
       The request is being prepared.
     :`active`:
       Cancellation activated.
     :`unsuccessful`:
       Cancellation was unsuccessful.

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

:reasonType:
    string

    There are four possible types for `reporting`, `aboveThresholdUA`, `aboveThresholdEU`, `esco`,
    `competitiveDialogueEU`, `competitiveDialogueUA`, `competitiveDialogueEU.stage2`, `competitiveDialogueUA.stage2`,
    `closeFrameworkAgreementUA`, `closeFrameworkAgreementSelectionUA` procedures set by procuring entity:

     :`noDemand`:
       No need in procurement of goods, works and services.

     :`unFixable`:
       Can not fix revealed violations of the law in the scope of public procurement.

     :`forceMajeure`:
       Can not do a procurement due to force majeure conditions.

     :`expensesCut`:
       Cut down the expenses of procurement of goods, works and services.

    Possible types for `negotiation` and `negotiation.quick`:

     :`noDemand`:
       No need in procurement of goods, works and services.

     :`unFixable`:
       Can not fix revealed violations of the law in the scope of public procurement.

     :`noObjectiveness`:
       Can not do a procurement due to force majeure conditions.

     :`expensesCut`:
       Cut down the expenses of procurement of goods, works and services.

     :`dateViolation`:
       Cut down the expenses of procurement of goods, works and services.

    Possible types for `belowThreshold` and `aboveThresholdUA.defense`:

     :`noDemand`:
       No need in procurement of goods, works and services.

     :`unFixable`:
       Can not fix revealed violations of the law in the scope of public procurement.

     :`expensesCut`:
       Cut down the expenses of procurement of goods, works and services.

:complaintPeriod:
    :ref:`period`

    The timeframe when complaints can be submitted.

:complaints:
    List of :ref:`complaint` objects


Cancellation workflow in :ref:`limited` and :ref:`openeu`
---------------------------------------------------------

.. graphviz::

    digraph G {
        A [ label="draft*" ]
        B [ label="pending" ]
        C [ label="active"]
        D [ label="unsuccessful" ]
        A -> {B,D};
        B -> {C,D};
    }

\* marks initial state


