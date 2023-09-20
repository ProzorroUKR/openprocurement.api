
.. include:: defs.hrst

.. index:: Buyer

.. _Buyer:

Buyer
=====

Schema
------

:name:
    string, multilingual

    |ocdsDescription|
    The common name of the organization.

:identifier:
    :ref:`Identifier`

    |ocdsDescription|
    The primary identifier for this organization.

:additionalIdentifiers:
    List of :ref:`identifier` objects

:address:
    :ref:`Address`, required

:signerInfo:
    :ref:`SignerInfo`
