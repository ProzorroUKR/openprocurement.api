
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

:dataSchema:
    string

    Determines the schema of data format in expectedValues.
    It is allowed only for `"dataType": "string"`

    Possible values are:
     :`ISO 639-3`:
       Format for `language codes <https://prozorroukr.github.io/standards/classifiers/languages.json>`_
     :`ISO 3166-1 alpha-2`:
       Format for `country codes <https://prozorroukr.github.io/standards/classifiers/countries.json>`_

:minValue:
    int/float

    |ocdsDescription|
    Used to state the lower bound of the requirement when the response must be within a certain range.

:maxValue:
    int/float

    |ocdsDescription|
    Used to state the higher bound of the requirement when the response must be within a certain range.

:expectedValue:
    int/float/bool

    |ocdsDescription|
    Used to state the requirement when the response must be particular value.

:expectedValues:
    string

    Used to state the requirement when the response must be an array of particular values.

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