.. _competitiveordering_tutorial:

Tutorial
========

Configuration
-------------

The set of possible configuration values:

.. csv-table::
   :file: csv/config.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

Creating tender
---------------

Tender `competitiveOrdering` has pre-selection procedure and has to be connected to agreement.

Let's use next agreement for our example:

.. http:example:: http/view-agreement-1-contract.http
   :code:

We can create tender connected to this agreement:

.. http:example:: http/tender-post-attempt-json-data.http
   :code:

Tender `competitiveOrdering` does not contain an appeal in the form of filing a complaint with the AMCU at any stage where such an appeal arises (follow configurations description :ref:`tender_complaints`, :ref:`award_complaints`, :ref:`cancellation_complaints`).

That's why there is no `complaintPeriod` in tender body after it was created.
If we try to add complaint about tender, we will see the error:

.. http:example:: http/tender-add-complaint-error.http
   :code:

Tender can contain only one lot. If we will try to add more than one lot, we will get error:

.. http:example:: http/tender-add-lot-more-than-1-error.http
   :code:

Also you will need to update data about item's related lots:

.. http:example:: http/tender-add-relatedLot-to-item.http
   :code:

Tender activating
-----------------

At first we needed to add EXCLUSION criteria to our tender(:ref:`About criteria you can read here<criteria_operation>`).

.. http:example:: http/add-exclusion-criteria.http
   :code:

Let's try to activate tender:

.. http:example:: http/tender-activating-insufficient-active-contracts-error.http
   :code:

You can see that we got error, because we have not enough active contracts in our agreement.

There is the list of all validation errors that can be raised during tender activation related to agreement:

* Agreement not found in agreements
* Agreement status is not active
* Agreement has less than 3 active contracts
* tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)

After adding more active contracts to our agreement let's make another attempt to activate tender:

.. http:example:: http/tender-activating.http
   :code:

You can see that tender was activated successfully.

.. note::
    Further steps for `competitiveOrdering` tender are the same as in :ref:`open`, you can follow corresponding tutorial :ref:`open_tutorial`.

Questions
----------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions:

.. http:example:: http/ask-question.http
   :code:

The difference between :ref:`open` procedure is that in `competitiveOrdering` only qualified suppliers from agreement may ask question.
If another author try to ask question, we will see error:

.. http:example:: http/ask-question-invalid-author.http
   :code:


Qualification complaints
-------------------------

As tender `competitiveOrdering` doesn't have the opportunity to add complaint about the decision on the qualifications of participants
if we try to add complaint about award, we will see the error:

.. http:example:: http/tender-add-complaint-qualification-error.http
   :code:

`complaintPeriod` is present in award as there is a period for adding claims during qualification:

.. http:example:: http/tender-get-award.http
   :code:


Cancellation complaints
------------------------

As tender `competitiveOrdering` doesn't have the opportunity to add complaint about the cancellation
if we try to add complaint about cancellation, we will see the error:

.. http:example:: http/tender-add-complaint-cancellation-error.http
   :code:

`complaintPeriod` is not present in cancellation. And after cancellation was transferred to status `pending`,
then cancellation will automatically update status to `active` and tender is being cancelled.

.. http:example:: http/pending-cancellation.http
   :code:
