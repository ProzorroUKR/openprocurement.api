.. _competitiveordering_long_tutorial:

Tutorial (long)
===============

Configuration
-------------

The set of possible configuration values:

.. csv-table::
   :file: csv/config-long.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

Creating tender
---------------

Tender `competitiveOrdering` has pre-selection procedure and has to be connected to agreement.

Let's use next agreement for our example:

.. http:example:: http/long/view-agreement-1-contract.http
   :code:

We can create tender connected to this agreement:

.. http:example:: http/long/tender-post-attempt-json-data.http
   :code:

Also you will need to update data about item's related lots:

.. http:example:: http/long/tender-add-relatedLot-to-item.http
   :code:

Tender activating
-----------------

At first we needed to add EXCLUSION criteria to our tender(:ref:`About criteria you can read here<criteria_operation>`).

.. http:example:: http/long/add-exclusion-criteria.http
   :code:

Let's try to activate tender:

.. http:example:: http/long/tender-activating-insufficient-active-contracts-error.http
   :code:

You can see that we got error, because we have not enough active contracts in our agreement.

There is the list of all validation errors that can be raised during tender activation related to agreement:

* Agreement not found in agreements
* Agreement status is not active
* Agreement has less than 3 active contracts
* tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)

Before activating tender it is required to add sign document to tender.
If there is no sign document during activation, we will see an error:

.. http:example:: http/long/notice-document-required.http
   :code:

Sign document should have `documentType: notice` and `title: *.p7s`. Let's add such document:

.. http:example:: http/long/add-notice-document.http
   :code:

After adding more active contracts to our agreement and sign document let's make another attempt to activate tender:

.. http:example:: http/long/tender-activating.http
   :code:

You can see that tender was activated successfully.

Questions
----------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions:

.. http:example:: http/long/ask-question.http
   :code:

The difference between :ref:`open` procedure is that in `competitiveOrdering` only qualified suppliers from agreement may ask question.
If another author try to ask question, we will see error:

.. http:example:: http/long/ask-question-invalid-author.http
   :code:


Active tendering period end
----------------------------

After tender period ended, CBD checks one more time status of contract for suppliers in agreement.
If contract status is still `active` - bid is getting `active` status too, in other cases - bid gets `invalid` status.

Let's imagine, after `active.tendering` period start, the bid with active contract in agreement was registered successfully:

.. http:example:: http/long/register-third-bid.http
   :code:

After that second contract supplier in agreement was disqualified during `active.tendering` period.

Let's see our bid status after `active.tendering` period ends. This bid was disqualified:

.. http:example:: http/long/active-tendering-end-not-member-bid.http
   :code:


Confirming qualification
------------------------

Qualification comission can set award to `active` or `unsuccessful` status.

There are validations before registering qualification decision:

* `qualified: True` - for setting award from `pending` to `active`

* `qualified: False` - for setting award from `pending` to `unsuccessful`

As `competitiveOrdering` doesn't have ARTICLE 17 criteria, it is forbidden to set field `eligible` for award.

.. note::
    Further steps for `competitiveOrdering` tender are the same as in :ref:`open`, you can follow corresponding tutorial :ref:`open_tutorial`.
