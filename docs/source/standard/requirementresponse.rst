
.. include:: defs.hrst

.. index:: RequirementResponse
.. _RequirementResponse:

RequirementResponse
===================

Schema
------

:id:
    uid, auto-generated

:title:
    string, multilingual, required

    |ocdsDescription|
    RequirementResponse title.

:description:
    string, multilingual

    |ocdsDescription|
    RequirementResponse description.

:period:
    :ref:`extendPeriod`

:requirement:
    :ref:`Reference`

    |ocdsDescription|
    The reference for tender requirement.

:relatedTenderer:
     :ref:`Reference`

    |ocdsDescription|
    The reference for organization.

:relatedItem:
    string

    Id of related :ref:`item`.

:evidences:
    List of :ref:`Evidence` objects

:values:
    List of strings

    The values should be from `requirement.expectedValues` field. This field should be set if requirement has `dataType: string`.

:value:
    boolean/int/decimal

    The value of this requirement response. The value must be of the type defined in the requirement.dataType field. This field should be set if requirement has `dataType` another from `string`.
