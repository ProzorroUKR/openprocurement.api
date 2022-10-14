.. _centralized_procurements:


Centralized procurements
========================


Creating plan procurement
-------------------------

Buyer creates a plan. He should specify himself in `buyers` list and point at one of the central procurement organizations in `procuringEntity` field:

.. http:example:: http/create-plan.http
   :code:


Creating approve milestone
--------------------------

As central procurement organization sees itself as `procuringEntity` of a plan,
it can post milestones to this plan:

    .. http:example:: http/post-plan-milestone.http
       :code:

Only if the access token from the response is provided, the milestone can be changed later:

    .. http:example:: http/patch-plan-milestone.http
       :code:

.. note::
    The fields you can update depend on current milestone status:
       - `dueDate` can only be updated at `scheduled` milestone status
       - `description` - either at `scheduled` or `met`

Posting documents is also require the milestone access token (as well as changing documents using PATCH/PUT methods):

    .. http:example:: http/post-plan-milestone-document.http
       :code:


Creating tender
---------------

The central procurement organization creates an aggregated tender in `draft` status
and specifies all the buyer organizations using `buyers` list of :ref:`PlanOrganization`:

.. http:example:: http/create-tender.http
   :code:


Connecting plans to the tender
------------------------------

The central procurement organization connects the plan to the tender.
If there are many plans, they should be connected one by one.


.. http:example:: http/post-tender-plans.http
    :code:


As a result the plan is moved to "complete" status

.. http:example:: http/plan-complete.http
    :code:


The tender `plans` field contains all the plan ids

.. http:example:: http/tender-get.http
    :code:


Creation of aggregate contracts
-------------------------------

For each `buyer` object in tender system is creating separate `contract` respectively when `award` become active.

Create tender with several buyers, each `item` should be assigned to related `buyer` using `relatedBuyer` field :

.. http:example:: ../contracting/http/create-multiple-buyers-tender.http
    :code:

Move forward as usual, activate award:

.. http:example:: ../contracting/http/set-active-award.http
    :code:

After activating award system is creating such amount of contracts that corresponds to the amount of buyers

.. http:example:: ../contracting/http/get-multi-contracts.http
    :code:

Update Amount.Value of each contract considering the sum of product of Unit.Value by Quantity for each item in contract.

.. http:example:: ../contracting/http/patch-1st-contract-value.http
    :code:

.. http:example:: ../contracting/http/patch-2nd-contract-value.http
    :code:

You can activate or terminate each contract as usual.
If there are not contracts in `pending` status and at least one contract became `active` tender is becoming `complete`

If award was cancelled, all contracts related to this awardID become in cancelled status.


Cancellation of aggregate contracts
-----------------------------------

Contracts can be cancelled:

.. http:example:: ../contracting/http/patch-to-cancelled-1st-contract.http
    :code:

Except when contract is the last not cancelled contract:

.. http:example:: ../contracting/http/patch-to-cancelled-2nd-contract-error.http
    :code:

In that case related award should be cancelled:

.. http:example:: ../contracting/http/set-active-award.http
    :code:

Let's check all contracts are cancelled:

.. http:example:: ../contracting/http/get-multi-contracts-cancelled.http
    :code:
