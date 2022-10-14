.. _tutorial_stage2EU:

Modifying tender
----------------

On first stage you set procurementMethodType to ``CompetitiveDialogueEU`` then on second stage you have tender which similar to Open UE procedure.

You can modify only ``tenderPeriod.endDate`` and ``deliveryDate`` for ``items``. Another changes will not be saved.
Let's update tender by supplementing it with all other essential properties:

.. http:example:: tutorial/stage2/EU/patch-tender-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properties have merged with existing tender data. Additionally, the dateModified property was updated to reflect the last modification timestamp.

Also we must set tender status to ``active.tendering`` for adding access to supplier

.. http:example:: tutorial/stage2/EU/tender-activate.http
   :code:


Checking the listing again reflects the new modification date:

.. http:example:: tutorial/stage2/EU/tender-listing-after-patch.http
   :code:

Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. http:example:: tutorial/stage2/EU/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. http:example:: tutorial/stage2/EU/update-tender-after-enqiery-with-update-periods.http
   :code:

.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. http:example:: tutorial/stage2/EU/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: tutorial/stage2/EU/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. http:example:: tutorial/stage2/EU/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. http:example:: tutorial/stage2/EU/tender-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. http:example:: tutorial/stage2/EU/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: tutorial/stage2/EU/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions:
Ask question can only participants which were approved on first stage, someone else try ask, he catch error

.. http:example:: tutorial/stage2/EU/ask-question-bad-participant.http
   :code:

Now participant from first stage try create question.

.. http:example:: tutorial/stage2/EU/ask-question.http
   :code:

Procuring entity can answer them:

.. http:example:: tutorial/stage2/EU/answer-question.http
   :code:

One can retrieve either questions list:

.. http:example:: tutorial/stage2/EU/list-question.http
   :code:

or individual answer:

.. http:example:: tutorial/stage2/EU/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. http:example:: tutorial/stage2/EU/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.
Bidder can register a bid with `draft` status.

Like with question only approved participants can register bid.
If participant which did not was on first stage try create bid, he will catch error

.. http:example:: tutorial/stage2/EU/try-register-bidder.http
   :code:

Get error, now participant from first stage try

.. http:example:: tutorial/stage2/EU/register-bidder.http
   :code:

and approve to pending status:

.. http:example:: tutorial/stage2/EU/activate-bidder.http
   :code:

Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal technical document(s):

.. http:example:: tutorial/stage2/EU/upload-bid-proposal.http
   :code:

Confidentiality
^^^^^^^^^^^^^^^

Documents can be either public or private:

  1. Privacy settings can be changed only for the latest version of the document.
  2. When you upload new version of the document, privacy settings are copied from the previous version.
  3. Privacy settings can be changed only during `tenderPeriod` (with `active.tendering` status).
  4. If tender has status `active.qualification` winner can upload only public documents.

Let's upload private document:

.. http:example:: tutorial/stage2/EU/upload-bid-private-proposal.http
   :code:

To define the document as "private" - `confidentiality` and `confidentialityRationale` fields should be set.

`confidentiality` field value can be either `buyerOnly` (document is private) or `public` (document is publicly accessible).

Content of private documents (`buyerOnly`) can be accessed only by procuring entity or by participant who uploaded them.

`confidentialityRationale` field is required only for private documents and should contain at least 30 characters.

Let's mark the document as "private":

.. http:example:: tutorial/stage2/EU/mark-bid-doc-private.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: tutorial/stage2/EU/bidder-documents.http
   :code:

.. _stage2EU_envelopes:

Financial documents uploading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Financial documents are also a part of Bid but are located in different end-points.

In order to create and/or get financial document ``financial_documents`` end-point should be used:

.. http:example:: tutorial/stage2/EU/upload-bid-financial-document-proposal.http
   :code:

Get financial documents:

.. http:example:: tutorial/stage2/EU/bidder-financial-documents.http
   :code:


`Financial` documents will be publicly accessible after the auction.

Here is bidder proposal with all documents.

.. http:example:: tutorial/stage2/EU/bidder-view-financial-documents.http
   :code:

Note that financial documents are stored in `financialDocuments` attributes of :ref:`Bid`.


Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. http:example:: tutorial/stage2/EU/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. http:example:: tutorial/stage2/EU/bidder-activate-after-changing-tender.http
   :code:

Second stage EU Competitive Dialogue procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage:

.. http:example:: tutorial/stage2/EU/register-2nd-bidder.http
   :code:

Batch-mode bid registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register one more bid with documents using single request (batch-mode):

.. http:example:: tutorial/stage2/EU/register-3rd-bidder.http
   :code:


.. index:: Awarding, Qualification

Bid Qualification
-----------------

On second stage in Competitive Dialogue procedure requires bid qualification.

Let's list qualifications:


.. http:example:: tutorial/stage2/EU/qualifications-listing.http
   :code:

Approve first two bids through qualification objects:

.. http:example:: tutorial/stage2/EU/approve-qualification1.http
   :code:

.. http:example:: tutorial/stage2/EU/approve-qualification2.http
   :code:

We can also reject bid:

.. http:example:: tutorial/stage2/EU/reject-qualification3.http
   :code:

And check that qualified bids are switched to `active`:

.. http:example:: tutorial/stage2/EU/qualificated-bids-view.http
   :code:

Rejected bid is not shown in `bids/` listing.

We can access rejected bid by id:

.. http:example:: tutorial/stage2/EU/rejected-bid-view.http
   :code:

Procuring entity approves qualifications by switching to next status:

.. http:example:: tutorial/stage2/EU/pre-qualification-confirmation.http
   :code:

You may notice 10 day stand-still time set in `qualificationPeriod`.

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. http:example:: tutorial/stage2/EU/auction-url.http
   :code:

Bidders can find out their participation URLs via their bids:

.. http:example:: tutorial/stage2/EU/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. http:example:: tutorial/stage2/EU/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification commission registers its decision via the following call:

.. http:example:: tutorial/stage2/EU/confirm-qualification.http
   :code:

Setting  contract value
-----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value.

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. http:example:: tutorial/stage2/EU/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. http:example:: tutorial/stage2/EU/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. http:example:: tutorial/stage2/EU/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

Let's upload contract document:

.. http:example:: tutorial/stage2/EU/tender-contract-upload-document.http
    :code:

`201 Created` response code and `Location` header confirm that this document was added.

Let's see the list of contract documents:

.. http:example:: tutorial/stage2/EU/tender-contract-get-documents.http
    :code:

We can upload another contract document:

.. http:example:: tutorial/stage2/EU/tender-contract-upload-second-document.http
    :code:

`201 Created` response code and `Location` header confirm that the second document was uploaded.

By default, document language is Ukrainian. You can can change it and set another language for the document
by assigning appropriate language code to the `language` field (available options: ``uk``, ``en``, ``ru``).
You can also set document's title (e.g. `title_en`) and description (e.g. `description_en`) fields.
See :ref:`Document` data structure for details.

.. http:example:: tutorial/stage2/EU/tender-contract-patch-document.http
    :code:

Let's see the list of all added contract documents:

.. http:example:: tutorial/stage2/EU/tender-contract-get-documents-again.http
    :code:

Let's view separate contract document:

.. http:example:: tutorial/stage2/EU/tender-contract-get.http
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

.. http:example:: tutorial/stage2/EU/update-cancellation-reasonType.http
   :code:

Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is required. Without documents you can't update tender status.

Upload the file contents

.. http:example:: tutorial/stage2/EU/upload-cancellation-doc.http
   :code:

Change the document description and other properties


.. http:example:: tutorial/stage2/EU/patch-cancellation.http
   :code:

Upload new version of the document


.. http:example:: tutorial/stage2/EU/update-cancellation-doc.http
   :code:

Passing Complaint Period
~~~~~~~~~~~~~~~~~~~~~~~~

For activate complaint period, you need to update cancellation from `draft` to `pending`.

.. http:example:: tutorial/stage2/EU/pending-cancellation.http
   :code:

When cancellation in `pending` status the tender owner is prohibited from all actions on the tender.

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if the complaint period(duration 10 days) is over and there were no complaints or
all complaints are canceled, then cancellation will automatically update status to `active`.

.. http:example:: tutorial/stage2/EU/active-cancellation.http
   :code:
