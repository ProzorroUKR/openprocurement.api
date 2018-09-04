.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Contract
.. _Contract:

Contract
========

Schema
------

:id:
    uid, auto-generated

:awardID:
    string, required

:bidID:
    string

:parameters:
    List of :ref:`Parameter` objects, auto-generated, read-only

:suppliers:
    List of :ref:`Organization` objects, auto-generated, read-only

:status:
    string, required

:date:
    string, :ref:`date`

    The date when the contract was changed or activated.

:unitPrices:
    List of :ref:`UnitPrice`
