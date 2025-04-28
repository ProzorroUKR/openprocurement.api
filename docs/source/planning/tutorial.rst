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

We see the added properties have merged with existing plan data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

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

Let's add budget breakdown and project to plan:

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


Plan rationale update
---------------------

The ``rationale`` field can be updated at any plan status:


.. http:example:: tutorial/complete-plan-rationale.http
   :code:


Plan fields history
-------------------

There is an endpoint that can show changes history of the certain fields.


At the moment only ``rationale`` is supported:


.. http:example:: tutorial/plan-rationale-history.http
   :code:


Plan of Ukraine
---------------

If the source of financing is indicated, the Customer may indicate the item of the Plan of Ukraine in `budget.project`.

If item is from dictionary `plan_of_ukraine <https://prozorroukr.github.io/standards/classifiers/plan_of_ukraine.json>`_ than there are additional validations for `name` and `name_en` fields:

.. http:example:: tutorial/patch-plan-budget-project-name-invalid.http
   :code:

Successful adding project from plan of Ukraine:

.. http:example:: tutorial/patch-plan-breakdown.http
   :code:

Ukraine facility
-----------------

For `state`, `local` and `crimea` budgets, the Customer should indicate the code of Ukraine facility's classifiers in `budget.breakdown.classification` and `budget.breakdown.address.addressDetails`.

*  For `state` budgets KPK dictionaries are used. They are divided by year, e.g. `KPK-2025 <https://github.com/ProzorroUKR/standards/blob/actions/classifiers/kpk_2025.json>`_.
*  For `local` and `crimea` budgets `KATOTTG <https://github.com/ProzorroUKR/standards/blob/actions/classifiers/katottg.json>`_ and  `TKPKMB <https://github.com/ProzorroUKR/standards/blob/actions/classifiers/tkpkmb.json>`_ dictionaries are used.

There are additional validations for these kinds of budget's breakdown:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-state-invalid.http
   :code:

Successful adding `classification` for `state` budget breakdown:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-state.http
   :code:

Let's look what we have for `local` budget breakdown:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local-invalid.http
   :code:

Let's add `classification` for `local` budget breakdown and see what happened:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local-address-required.http
   :code:

Let's add address, KATOTTG is required for `local` budget:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local-address-invalid.http
   :code:

Successful adding `classification` and `address` for `local` budget breakdown:

.. http:example:: tutorial/patch-plan-budget-breakdown-classifications-local.http
   :code:
