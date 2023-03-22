
.. _agreement_framework_tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/agreements` endpoint:

.. http:example:: http/agreements-listing-0.http
   :code:

Just invoking it reveals an empty set.

Agreement is transferred from the tender system by an automated process.


.. index:: Agreements

Creating agreement
------------------

Let's say that we have conducted framework, submission and qualification and it has ``active`` status. When the framework is active and you change qualification status to active, system **automatically** created agreement(from framework) with contract(from qualification).

Getting agreement
-----------------

Let's see our created framework:

.. http:example:: http/example-framework.http
   :code:

In our framework you can see the `agreementID` field where stores id of related agreement.
When we know id of our agreement we can get it:

.. http:example:: http/agreement-view.http
   :code:


Modifying agreement
-------------------

All operation with agreement can make `framework_owner`.
Only one thing that can make `framework_owner` is create/modify contract milestones.

Contract - object that stores information about participant

Milestone - that's contract history.

Contract ban
~~~~~~~~~~~~

For ban contract, you just need to add milestone to contract with type `ban`:

.. http:example:: http/milestone-ban-post.http
   :code:

You can see that contract status was automatically changed to `suspended`:

.. http:example:: http/agreement-view-contract-suspended.http
   :code:

After `dueDate` date of milestone, contract will be automatically set back to `active` status.

.. http:example:: http/agreement-view-contract-active.http
   :code:

Contract disqualify
~~~~~~~~~~~~~~~~~~~

You can see that contract was automatically created with `activation` milestone.

Field `dueDate` was automatically set with `period.endDate` date.
On that date milestone will be automatically set to `met` status, and contract will switched status to `terminated`.

When you want to manually disqualify contract, you need to manually set `activation` milestone status to `met`:

.. http:example:: http/milestone-activation-patch.http
   :code:

Now you can see that contract status was changed to `terminated`:

.. http:example:: http/agreement-view-contract-terminated.http
   :code:

Finishing agreement
~~~~~~~~~~~~~~~~~~~

Lets wait for `period.endDate` date and see what will happen:

.. http:example:: http/agreement-view-terminated.http
   :code:

You can see that `activation` milestone was automatically set to `met` status, contract status was changed to `terminated` and agreement status was changed to `terminated`.
