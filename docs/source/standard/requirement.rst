
.. include:: defs.hrst

.. index:: Requirement
.. _requirement:

Requirement
===========

Schema
------

:id:
    uid, auto-generated

:title:
    string, multilingual, required

    |ocdsDescription|
    Requirement title.

:status:
    string

    Possible values are:

    * `active`
    * `cancelled`

    |ocdsDescription|
    Requirement status (`active` by default).

:description:
    string, multilingual

    |ocdsDescription|
    Requirement description.

:dataType:
    string, required

    |ocdsDescription|
    Determines the type of response.

    Possible values are:
     :`string`:
       The requirement response must be of type string
     :`number`:
       The requirement response must be of type number
     :`integer`:
       The requirement response must be of type integer
     :`boolean`:
       The requirement response must be of type boolean

:minValue:
    string

    |ocdsDescription|
    Used to state the lower bound of the requirement when the response must be within a certain range.

:maxValue:
    string

    |ocdsDescription|
    Used to state the higher bound of the requirement when the response must be within a certain range.

:expectedValue:
    string

    |ocdsDescription|
    Used to state the requirement when the response must be particular value.

:period:
    :ref:`extendPeriod`

:relatedFeature:
    string

    Id of related :ref:`Feature`.

:eligibleEvidences:
    List of :ref:`EligibleEvidence` objects.

:datePublished:
    string, :ref:`date`

    |ocdsDescription|
    The date on which the requirement version was published.

:dateModified:
    string, :ref:`date`

    |ocdsDescription|
    Date that the requirement version was cancelled