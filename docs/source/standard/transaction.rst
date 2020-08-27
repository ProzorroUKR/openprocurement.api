
.. include:: defs.hrst

.. index:: Transaction

.. _Transaction:

Transaction
===========

Schema
------

:id:
    string, required

    A unique identifier for this transaction.

:documents:
    List of :ref:`Document` objects

    Used to point either to a corresponding Fiscal Data Package, IATI file, or machine or human-readable source

:date:
    string, :ref:`date`, required

    The date of the transaction.

:value:
    string, :ref:`Guarantee`, required

    The value of the transaction.

:payer:
    :ref:`OrganizationReference`, required

    An organization reference for the organization from which the funds in this transaction originate.

:payee:
    :ref:`OrganizationReference`, required

    An organization reference for the organization which receives the funds in this transaction.

:status:
    string, required

    The current status of transaction.
