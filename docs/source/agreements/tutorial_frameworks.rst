
.. _agreement_framework_tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/agreements` endpoint:

.. include:: http/frameworks/agreements-listing-0.http
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

.. include:: http/frameworks/example-framework.http
   :code:

In our framework you can see the `agreementID` field where stores id of related agreement.
When we know id of our agreement we can get it:

.. include:: http/frameworks/agreement-view.http
   :code:


Modifying agreement
-------------------

All operation with agreement can make `framework_owner`.
Only one thing that can make `framework_owner` is create contract milestones.

Contract - object that stores information about participant

Milestone - that's contract history.

Contract ban
~~~~~~~~~~~~

For ban contract, you just need to add milestone to contract with status `ban`:

.. include:: http/frameworks/post-milestone-ban.http
   :code:
