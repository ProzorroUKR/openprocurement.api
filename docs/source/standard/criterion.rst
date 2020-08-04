
.. include:: defs.hrst

.. index:: Criterion
.. _criterion:

Criterion
=========

Schema
------

:id:
    uid, auto-generated

:title:
    string, multilingual, required

    |ocdsDescription|
    Criterion title.

:description:
    string, multilingual

    |ocdsDescription|
    Criterion description.

:source:
    string

    |ocdsDescription|
    Source of response to the requirements specified in the criterion. For example, responses might be submitted by tenderers or by an assessment committee at the procuringEntity.

    Possible values are:
     :`tenderer`:
       Default. The response is provided by the tenderer.
     :`buyer`:
       The response is provided by the buyer.
     :`procuringEntity`:
       The response is provided by the procuring entity.
     :`ssrBot`:
       The response is provided by the bot.
     :`winner`:
       The response is provided by the winner.

:relatesTo:
    string

    |ocdsDescription|
    The schema element that the criterion judges, evaluates or assesses. For example, the criterion might be defined against items or against bidders.

    Possible values are:
     :`tenderer`:
       Default. The criterion evaluates or assesses a tenderer.
     :`item`:
       The criterion evaluates or assesses a item.
     :`lot`:
       The criterion evaluates or assesses a lot.

:relatedItem:
    string

    :`if relatesTo == tender`:
      Should be None.
    :`if relatesTo == item`:
      Id of related :ref:`item`.
    :`if relatesTo == lot`:
      Id of related :ref:`lot`.

:classification:
    :ref:`Classification`

    |ocdsDescription|
    The primary classification for the item.

:additionalClassifications:
    List of :ref:`Classification` objects

    |ocdsDescription|
    An array of additional classifications for the item.

:legislation:
    List of :ref:`LegislationItem` objects.

:requirementGroups:
    List of :ref:`RequirementGroup` objects.
