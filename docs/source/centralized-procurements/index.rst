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


Aggregate contracts
-------------------

All operations with aggregated contracts moved to :ref:`econtracting`