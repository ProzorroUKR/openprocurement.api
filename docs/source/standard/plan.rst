.. include:: defs.hrst
.. index:: Plan, PlanOrganization, PlanTender, Budget, Project, BudgetPeriod
.. _plan:

Plan
====

planID
------
   string, auto-generated, read-only

   The plan identifier to refer plan to in "paper" documentation.

   |ocdsDescription|
   planID should always be the same as the OCID. It is included to make the flattened data structure more convenient.

procuringEntity
---------------

   :ref:`PlanOrganization`, required

   Organization conducting the tender.

   |ocdsDescription|
   The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.

status
------

   string

   Possible values:
        * draft
        * scheduled
        * cancelled
        * complete

   Status of the Plan.

   .. graphviz::

        digraph G {

            rankdir = LR

            draft [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = cadetblue1
            ]
            scheduled [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = deepskyblue1
            ]
            complete [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = aquamarine3
            ]
            cancelled [
                shape = circle
                fixedsize = true
                width = .9
                style = filled
                fillcolor = coral1
            ]

            draft -> scheduled
            scheduled -> complete
            scheduled -> cancelled
        }

buyers
------
   List of :ref:`PlanOrganization` objects, required at least 1 object

   Identifications of the subjects in whose interests the purchase is made

   Validation depends on:

        * :ref:`PLAN_BUYERS_REQUIRED_FROM` constant


milestones
----------

   List of :ref:`PlanMilestone` objects

   Milestones of type `approval` used to provide Central procurement organization approve feature

   Validation depends on:

        * :ref:`MILESTONES_VALIDATION_FROM` constant

tender
------
   :ref:`PlanTender`, required

   Data regarding tender process.

budget
------
   :ref:`Budget`, required (except `tender.procurementMethodType` is `"esco"`).

   Total available tender budget.

   |ocdsDescription|
   The total estimated value of the procurement.



classification
--------------

    :ref:`Classification`, required

    |ocdsDescription|
    The primary classification for the item. See the
    itemClassificationScheme to identify preferred classification lists,
    including CPV and GSIN.

    It is mandatory for `classification.scheme` to be `CPV` or `ДК021`. The
    `classification.id` should be valid CPV or ДК021 code.

additionalClassifications
-------------------------

    List of :ref:`Classification` objects

    |ocdsDescription|
    An array of additional classifications for the item. See the
    itemClassificationScheme codelist for common options to use in OCDS.
    This may also be used to present codes from an internal classification
    scheme.

    Item wich classification.id starts with 336 and contains
    additionalClassification objects have to contain no more than one
    additionalClassifications with scheme=INN.

    Item with classification.id=33600000-6 have to contain exactly one
    additionalClassifications with scheme=INN.

    It is mandatory to have at least one item with `ДКПП` as `scheme`.

documents
---------
   List of :ref:`document` objects

   |ocdsDescription|
   All documents and attachments related to the tender.

.. _tender_id:

tender_id
---------

   string, auto-generated, read-only

   ``id`` of the linked tender object. See :ref:`tender-from-plan`

items
-----
   list of :ref:`item` objects, required

   List that contains single item being procured.

   |ocdsDescription|
   The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.

cancellation
------------

    :ref:`PlanCancellation`

milestones
----------
   List of :ref:`PlanMilestone` objects

dateModified
------------
   string, :ref:`date`, auto-generated

datePublished
-------------
   string, :ref:`date`, auto-generated

owner
-----
    string, auto-generated

revisions
---------
   List of :ref:`revision` objects, auto-generated

   Historical changes to Tender object properties.


-----------


.. _PlanTender:

PlanTender
==========


procurementMethod
-----------------
    string

    Possible values:
        * ''
        * 'open'
        * 'limited'

    Procurement Method of the Tender.


procurementMethodType
---------------------
    string
    Possible values for `procurementMethod` == `''`:

    * '' - Without using an electronic system
    * 'centralizedProcurement' - Procurement via Central Purchasing Body

    Possible values for `procurementMethod` == `'open'`:

    * belowThreshold
    * aboveThresholdUA
    * aboveThresholdEU
    * aboveThresholdUA.defense
    * esco
    * closeFrameworkAgreementUA
    * competitiveDialogueEU
    * competitiveDialogueUA

    Possible values for `procurementMethod` == `'limited'`:

    * reporting
    * negotiation
    * negotiation.quick


tenderPeriod
------------
   :ref:`period`, required

   Period when bids can be submitted. At least `endDate` has to be provided.

   |ocdsDescription|
   The period when the tender is open for submissions. The end date is the closing date for tender submissions.

-----------

.. _Budget:

Budget
======

id
--
    string, required

description
-----------
    string, multilingual, required

amount
------
    float, required

amountNet
---------
    float, required

currency
--------
    string, required, length = 3

project
-------
    :ref:`Project`

period
------
    :ref:`BudgetPeriod`

    Validation depends on:

        * :ref:`BUDGET_PERIOD_FROM` constant

year
----
    integer, >=2000, deprecated in favor of `period`_

    Validation depends on:

        * :ref:`BUDGET_PERIOD_FROM` constant

notes
-----
    string

breakdown
---------
    List of :ref:`BudgetBreakdown`, required (except `tender.procurementMethodType` is `"belowThreshold"`, `"reporting"`, `"esco"`, `""`)


-----------


.. _Project:

Project
=======

id
--
    string, required

name
----
    string, multilingual, required

-----------

.. _BudgetPeriod:

BudgetPeriod
============

startDate
---------
    string, required, :ref:`date`

    |ocdsDescription|
    The start date for the period.

endDate
-------
    string, required, :ref:`date`

    |ocdsDescription|
    The end date for the period.

`startDate` should always precede `endDate`.

.. _BudgetBreakdown:

BudgetBreakdown
===============

:id:
    uid, auto-generated

:title:
    string, required

    Possible values are:

    * `state`
    * `crimea`
    * `local`
    * `own`
    * `fund`
    * `loan`
    * `other`

:description:
    string, multilingual, required if title == `other`

    Detailed description of budget breakdown.

:value:
    :ref:`Guarantee`

    Budget breakdown value

    Currency should be identical for all budget breakdown values and budget

    Sum of the breakdown values amounts can't be greater than budget amount  (except `tender.procurementMethodType` is `"esco"`)
