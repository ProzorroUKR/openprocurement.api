.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Tender, Auction
.. _shortlistedFirms:

shortlistedFirms
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

   list of :ref:`lots` objects.

   |ocdsDescription|
   List of lots

lots
====

Schema
------

:id:
    :ref:`lot`

    |ocdsDescription|
    The primary identifier for lot.