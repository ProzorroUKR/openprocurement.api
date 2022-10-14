.. _centralized_procurements:


Centralized procurements
========================


Creating plan procurement
-------------------------

Buyer creates a plan. He should specify himself in `buyers` list and point at one of the central procurement organizations in `procuringEntity` field:

.. httpexample:: http/create-plan.http
   :code:


Creating approve milestone
--------------------------

As central procurement organization sees itself as `procuringEntity` of a plan,
it can post milestones to this plan:

    .. httpexample:: http/post-plan-milestone.http
       :code:

Only if the access token from the response is provided, the milestone can be changed later:

    .. httpexample:: http/patch-plan-milestone.http
       :code:

.. note::
    The fields you can update depend on current milestone status:
       - `dueDate` can only be updated at `scheduled` milestone status
       - `description` - either at `scheduled` or `met`

Posting documents is also require the milestone access token (as well as changing documents using PATCH/PUT methods):

    .. httpexample:: http/post-plan-milestone-document.http
       :code:


Creating tender
---------------

The central procurement organization creates an aggregated tender in `draft` status
and specifies all the buyer organizations using `buyers` list of :ref:`PlanOrganization`:

.. httpexample:: http/create-tender.http
   :code:


Connecting plans to the tender
------------------------------

The central procurement organization connects the plan to the tender.
If there are many plans, they should be connected one by one.


.. httpexample:: http/post-tender-plans.http
    :code:


As a result the plan is moved to "complete" status

.. httpexample:: http/plan-complete.http
    :code:


The tender `plans` field contains all the plan ids

.. httpexample:: http/tender-get.http
    :code:


Creation of aggregate contracts
-------------------------------

For each `buyer` object in tender system is creating separate `contract` respectively when `award` become active.

Create tender with several buyers, each `item` should be assigned to related `buyer` using `relatedBuyer` field :

.. httpexample:: ../contracting/http/create-multiple-buyers-tender.http
    :code:

Move forward as usual, activate award:

.. httpexample:: ../contracting/http/set-active-award.http
    :code:

After activating award system is creating such amount of contracts that corresponds to the amount of buyers

.. httpexample:: ../contracting/http/get-multi-contracts.http
    :code:

Update Amount.Value of each contract considering the sum of product of Unit.Value by Quantity for each item in contract.

.. httpexample:: ../contracting/http/patch-1st-contract-value.http
    :code:

.. httpexample:: ../contracting/http/patch-2nd-contract-value.http
    :code:

You can activate or terminate each contract as usual.
If there are not contracts in `pending` status and at least one contract became `active` tender is becoming `complete`

If award was cancelled, all contracts related to this awardID become in cancelled status.


Cancellation of aggregate contracts
-----------------------------------

Contracts can be cancelled:

.. httpexample:: ../contracting/http/patch-to-cancelled-1st-contract.http
    :code:

Except when contract is the last not cancelled contract:

.. httpexample:: ../contracting/http/patch-to-cancelled-2nd-contract-error.http
    :code:

In that case related award should be cancelled:

.. httpexample:: ../contracting/http/set-active-award.http
    :code:

Let's check all contracts are cancelled:

.. httpexample:: ../contracting/http/get-multi-contracts-cancelled.http
    :code:
