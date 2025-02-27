
.. include:: defs.hrst

.. index:: ItemAttribute

.. _ItemAttribute:

ItemAttribute
=============

Schema
------

:name:
    string, required

:unit:
    :ref:`Unit`

:values:
    List of strings

    The values should be from `requirement.expectedValues` field.

:value:
    boolean/int/decimal

    The value of attribute. The value must be of the type defined in the requirement.dataType field.
