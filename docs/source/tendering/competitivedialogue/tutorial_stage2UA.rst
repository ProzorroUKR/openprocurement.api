.. _tutorial_stage2UA:


If on first stage you set ``procurementMethodType`` to ``CompetitiveDialogueUA``
then on second stage you have tender witch similar to Open UA procedure

Modifying tender
----------------


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

And activate a bid:

.. http:example:: tutorial/stage2/UA/activate-bidder.http
   :code:

Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal document(s):

.. http:example:: tutorial/stage2/UA/upload-bid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: tutorial/stage2/UA/bidder-documents.http
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

Qualification commission registers its decision via the following call:

.. http:example:: tutorial/stage2/UA/confirm-qualification.http
   :code:

Setting contract value
----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value.

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. http:example:: tutorial/stage2/UA/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. http:example:: tutorial/stage2/UA/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. http:example:: tutorial/stage2/UA/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

You can upload contract documents for the second stage Competitive Dialogue procedure.

Let's upload contract document:

.. http:example:: tutorial/stage2/UA/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that this document was added.

Let's view the uploaded contract document:

.. http:example:: tutorial/stage2/UA/tender-contract-get.http
   :code:


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
