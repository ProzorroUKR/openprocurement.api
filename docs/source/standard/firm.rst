
.. include:: defs.hrst

.. index:: Tender, Auction
.. _Firm:

Firm
================

Schema
------

:name:
    string, firm name, required

:identifier:
    :ref:`Identifier`

    |ocdsDescription|
    The primary identifier for this organization.

:lots:

   list of :ref:`LotId` objects.

   |ocdsDescription|
   List of lots


.. _LotId:

LotId
=====

Schema
------

:id:
    :ref:`lot`

    |ocdsDescription|
    The primary identifier for lot.
