.. _planning_tutorial:

Tutorial
========

Creating plan procurement
-------------------------

We strongly recommend creating plans in `draft` status.

Let’s create a plan:

.. http:example:: tutorial/create-plan.http
   :code:

We have `201 Created` response code, `Location` header and body with extra `id`, `planID`, and `dateModified` properties.

The second step is moving the plan to `scheduled` status so that it becomes actually published:

.. http:example:: tutorial/patch-plan-status-scheduled.http
   :code:

Let's check what plan registry contains:

.. http:example:: tutorial/plan-listing.http
   :code:

We do see the internal `id` of a plan (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/plans/`) and its `dateModified` datestamp.


Modifying plan
--------------

Let's update plan by supplementing it with all other essential properties:

.. http:example:: tutorial/patch-plan-procuringEntity-name.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing plan data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: tutorial/plan-listing-after-patch.http
   :code:

.. _tender-from-plan:


Tender creation from a procurement plan
---------------------------------------

A tender can be created from your procurement plan. This tender will be linked with the plan
using :ref:`tender's plans <tender>` and :ref:`plan's tender_id <tender_id>` fields.

.. note::
    | System failures during tender-from-plan creation can produce tenders that are not linked with their plans by :ref:`tender_id`.
    | Make sure you do use :ref:`2pc` and do not proceed with these error state tender objects (create new ones).


There are validation rules that are supposed to decline the chance of making a mistake

.. http:example:: tutorial/tender-from-plan-validation.http
   :code:

There are three of them:

    * procurementMethodType
    * procuringEntity.identifier - matching id and scheme with the same fields in tender data
    * classification.id  - matching with tender item classification codes using first 4 digits (``336`` is exception)

Plan should contain budget breakdown, otherwise it will be an error during tender creation:

.. http:example:: tutorial/tender-from-plan-breakdown.http
   :code:

Let's add budget breakdown to plan:

.. http:example:: tutorial/patch-plan-breakdown.http
   :code:

A successful example looks like this:

.. http:example:: tutorial/tender-from-plan.http
   :code:

Let's check that the plan status was switched to `complete`:

.. http:example:: tutorial/get-complete-plan.http
   :code:

After tender was created from plan it's no longer allowed to change plan:

.. http:example:: tutorial/tender-from-plan-readonly.http
   :code:



Plan completing without tendering
---------------------------------

There is a way to complete a plan without tender creation:

.. http:example:: tutorial/complete-plan-manually.http
   :code:

This only works if `procurementMethodType` is one of the following:

    * ``belowThreshold``
    * ``reporting``
    * empty string


Plan cancellation
-----------------

A plan can be cancelled using :ref:`plancancellation`:

.. http:example:: tutorial/plan-cancellation.http
   :code:

Making the cancellation object ``active`` cancels the plan:

.. http:example:: tutorial/plan-cancellation-activation.http
   :code:
