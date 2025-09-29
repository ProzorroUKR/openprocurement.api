
.. include:: defs.hrst

.. index:: EContractCancellation
.. _econtractcancellation:

EContractCancellation
======================

Schema
------

:id:
    uid, auto-generated

:reason:
    string, required

    The reason, why contract is being cancelled.

:reasonType:
    string

    There are possible values:

    * `requiresChanges`
    * `signingRefusal`

:status:
    string

    Possible values are:
     :`pending`:
       The request is being prepared.
     :`active`:
       Cancellation activated.

:dateCreated:
    string, auto-generated, :ref:`date`

    Date of cancellation creation.

:author:
    string, auto-generated

    The author of the cancellation

