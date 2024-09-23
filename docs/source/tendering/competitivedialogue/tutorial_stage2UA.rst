.. _tutorial_stage2UA:

Configuration
-------------

The set of possible configuration values:

.. csv-table::
   :file: csv/config-ua-stage2.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

Modifying tender
----------------

If on first stage you set ``procurementMethodType`` to ``CompetitiveDialogueUA``
then on second stage you have tender witch similar to Open UA procedure

You can modify only ``tenderPeriod.endDate`` and ``deliveryDate`` for ``items``. Another changes will not be saved.
Let's update tender by supplementing it with all other essential properties:

.. http:example:: tutorial/stage2/UA/patch-tender-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: tutorial/stage2/UA/tender-listing-after-patch.http
   :code:


Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. http:example:: tutorial/stage2/UA/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. http:example:: tutorial/stage2/UA/update-tender-after-enqiery-with-update-periods.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. http:example:: tutorial/stage2/UA/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: tutorial/stage2/UA/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. http:example:: tutorial/stage2/UA/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. http:example:: tutorial/stage2/UA/tender-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. http:example:: tutorial/stage2/UA/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: tutorial/stage2/UA/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions.
Ask question can only participants which were approved on first stage, someone else try ask, he catch error:

.. http:example:: tutorial/stage2/UA/ask-question-bad-participant.http
   :code:


.. http:example:: tutorial/stage2/UA/ask-question.http
   :code:

Procuring entity can answer them:

.. http:example:: tutorial/stage2/UA/answer-question.http
   :code:

One can retrieve either questions list:

.. http:example:: tutorial/stage2/UA/list-question.http
   :code:

or individual answer:

.. http:example:: tutorial/stage2/UA/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. http:example:: tutorial/stage2/UA/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.

Like with question only approved participants can register bid.
First participant witch didn't was on first stage try create bid.

.. http:example:: tutorial/stage2/UA/try-register-bidder.http
   :code:

Bidder can register a bid with draft status:

.. http:example:: tutorial/stage2/UA/register-bidder.http
   :code:

Then bidder should approve bid with pending status. If `tenderers.identifier.scheme = 'UA-EDR'` it is required to add sign document to bid.
If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/stage2/UA/activate-bidder-without-proposal.http
   :code:

Sign document should have `documentType: proposal` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/stage2/UA/upload-bid-proposal.http
   :code:

Let's try to activate bid one more time:

.. http:example:: tutorial/stage2/UA/activate-bidder.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: tutorial/stage2/UA/bidder-documents.http
   :code:

If we patched some fields in pending bid, then bid becomes `invalid` and should be signed one more time:

.. http:example:: tutorial/stage2/UA/patch-pending-bid.http
   :code:

If we try to activate bidder the new sign will be needed:

.. http:example:: tutorial/stage2/UA/activate-bidder-without-sign.http
   :code:

Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. http:example:: tutorial/stage2/UA/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. http:example:: tutorial/stage2/UA/bidder-activate-after-changing-tender.http
   :code:


Second stage Competitive Dialogue UA procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage.

Batch-mode bid registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register one more bid with documents using single request (batch-mode):

.. http:example:: tutorial/stage2/UA/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. http:example:: tutorial/stage2/UA/auction-url.http
   :code:

Bidders can find out their participation URLs via their bids:

.. http:example:: tutorial/stage2/UA/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. http:example:: tutorial/stage2/UA/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification comission can set award to `active` or `unsuccessful` status.

There are validations before registering qualification decision:

* `eligible: True` and `qualified: True` - for setting award from `pending` to `active`

* `eligible: False` and `qualified: True` OR `eligible: True` and `qualified: False` OR `eligible: False` and `qualified: False` - for setting award from `pending` to `unsuccessful`

Let's try to set `unsuccessful` status for `qualified` and `eligible` award and we will see an error:

.. http:example:: tutorial/stage2/UA/unsuccessful-qualified-award.http
   :code:

Let's try to set `active` status for `non-qualified` or `non-eligible` award and we will see an error:

.. http:example:: tutorial/stage2/UA/activate-non-qualified-award.http
   :code:

Before making decision it is required to add sign document to award.
If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/stage2/UA/award-notice-document-required.http
   :code:

The same logic for `unsuccessful` status:

.. http:example:: tutorial/stage2/UA/award-unsuccessful-notice-document-required.http
   :code:

Sign document should have `documentType: notice` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/stage2/UA/award-add-notice-document.http
   :code:

Qualification commission registers its decision via the following call:

.. http:example:: tutorial/stage2/UA/confirm-qualification.http
   :code:


.. index:: Setting Contract

Setting Contract
----------------

In EContracting the contract is created directly in contracting system.

.. note::
    Some of data will be mirrored to tender until contract will be activated for backward compatibility.

Read more about working with EContracting in contracting system in :ref:`econtracting_tutorial` section.


Cancelling tender
-----------------

Tender creator can cancel tender anytime. The following steps should be applied:

1. Prepare cancellation request.
2. Fill it with the protocol describing the cancellation reasons.
3. Passing complaint period(10 days)
4. Cancel the tender with the prepared reasons.

Only the request that has been activated (th step above) has power to
cancel tender.  I.e.  you have to not only prepare cancellation request but
to activate it as well.

For cancelled cancellation you need to update cancellation status to `unsuccessful`
from `draft` or `pending`.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tender creator can cancel tender anytime (except when tender in status `active.auction` or in terminal status e.g. `unsuccessful`, `canceled`, `complete`).

The following steps should be applied:

There are four possible types of cancellation reason - tender was `noDemand`, `unFixable`, `forceMajeure` and `expensesCut`.

`id` is autogenerated and passed in the `Location` header of response.

.. http:example:: tutorial/stage2/EU/prepare-cancellation.http
   :code:

You can change ``reasonType`` value to any of the above.

.. http:example:: tutorial/stage2/UA/update-cancellation-reasonType.http
   :code:

Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is required. Without documents you can't update tender status.

Upload the file contents

.. http:example:: tutorial/stage2/UA/upload-cancellation-doc.http
   :code:

Change the document description and other properties


.. http:example:: tutorial/stage2/UA/patch-cancellation.http
   :code:

Upload new version of the document


.. http:example:: tutorial/stage2/UA/update-cancellation-doc.http
   :code:

Passing Complaint Period
~~~~~~~~~~~~~~~~~~~~~~~~

For activate complaint period, you need to update cancellation from `draft` to `pending`.

.. http:example:: tutorial/stage2/UA/pending-cancellation.http
   :code:

When cancellation in `pending` status the tender owner is prohibited from all actions on the tender.

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if the complaint period(duration 10 days) is over and there were no complaints or
all complaints are canceled, then cancellation will automatically update status to `active`.

.. http:example:: tutorial/stage2/UA/active-cancellation.http
   :code:
