
.. include:: defs.hrst

.. index:: Framework
.. _framework:

Framework
=========

Schema
------

:title:
   string, multilingual

   The name of the framework, displayed in listings.

:description:
   string, multilingual

   Detailed description of framework.

:prettyID:
   string, auto-generated, read-only

   The framework identifier.


:procuringEntity:
   :ref:`ProcuringEntity`, required

   Organization conducting the framework.

   If :code:`frameworkType` is :code:`electronicCatalogue`, then possible values of :code:`ProcuringEntity.kind` are limited to :code:`['central']`.


:frameworkType:
    string

    :`electronicCatalogue`:
        Framework for electronic catalog process


:date:
    string, :ref:`date`, auto-generated


:documents:
   List of :ref:`document` objects

   |ocdsDescription|
   All documents and attachments related to the framework.

:enquiryPeriod:
   :ref:`period`, read-only, auto-generated

   Period when questions are allowed.

   |ocdsDescription|
   The period during which enquiries may be made and will be answered.

   If :code:`frameworkType` is :code:`electronicCatalogue`, then suppliers cannot add submissions in this period.

:dateModified:
    string, :ref:`date`, auto-generated

:owner:
    string, auto-generated

:period:
   :ref:`period`, read-only, auto-generated

   Period when submissions can be submitted.

   |ocdsDescription|
   The period when the framework is open for submissions.

:qualificationPeriod:
   :ref:`period`, required

   Period when submissions can be qualified. At least `endDate` has to be provided.

    If :code:`frameworkType` is :code:`electronicCatalogue`, then :code:`qualificationPeriod` can be from 30 to 1095 days long.


:status:
   string

   :`draft`:
      If :code:`frameworkType` is :code:`electronicCatalogue`, then in this status any fields of framework can be changed.
   :`active`:
      If :code:`frameworkType` is :code:`electronicCatalogue`, then in this status only :code:`contactPoint`, :code:`qualificationPeriod.endDate`, :code:`description` and :code:`documents` fields of framework can be changed.
   :`unsuccessful`:
      Terminal status. Framework can become `unsuccessful` if there was no submissions in first 20 full working days from framework activation.
   :`complete`:
      Complete framework.

   Status of the Framework.


:classification:
   :ref:`Classification`, required

   |ocdsDescription|
   The primary classification for the framework.

   If :code:`frameworkType` is :code:`electronicCatalogue`, then it is mandatory for `classification.scheme` to be `ДК021`. The `classification.id` should be valid ДК021 code.


:additionalClassification:
   List of :ref:`Classification` objects

   |ocdsDescription|
   An array of additional classifications for the framework.


:revisions:
   List of :ref:`revision` objects, auto-generated

   Historical changes to Framework object properties.
