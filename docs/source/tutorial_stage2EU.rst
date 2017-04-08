.. _tutorial_stage2EU:

Modifying tender
----------------

On first stage you set procurementMethodType to ``CompetitiveDialogueEU`` then on second stage you have tender which similar to Open UE procedure.

You can modify only ``tenderPeriod.endDate`` and ``deliveryDate`` for ``items``. Another changes will not be saved.
Let's update tender by supplementing it with all other essential properties:

.. include:: tutorial/stage2/EU/patch-tender-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properties have merged with existing tender data. Additionally, the dateModified property was updated to reflect the last modification timestamp.

Also we must set tender status to ``active.tendering`` for adding access to supplier

.. include:: tutorial/stage2/EU/tender-activate.http
   :code:


Checking the listing again reflects the new modification date:

.. include:: tutorial/stage2/EU/tender-listing-after-patch.http
   :code:

Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. include:: tutorial/stage2/EU/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. include:: tutorial/stage2/EU/update-tender-after-enqiery-with-update-periods.http
   :code:

.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/stage2/EU/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/stage2/EU/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: tutorial/stage2/EU/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/stage2/EU/tender-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/stage2/EU/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/stage2/EU/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions:
Ask question can only participants which were approved on first stage, someone else try ask, he catch error

.. include:: tutorial/stage2/EU/ask-question-bad-participant.http
   :code:

Now participant from first stage try create question.

.. include:: tutorial/stage2/EU/ask-question.http
   :code:

Procuring entity can answer them:

.. include:: tutorial/stage2/EU/answer-question.http
   :code:

One can retrieve either questions list:

.. include:: tutorial/stage2/EU/list-question.http
   :code:

or individual answer:

.. include:: tutorial/stage2/EU/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. include:: tutorial/stage2/EU/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.
Bidder can register a bid with `draft` status.

Like with question only approved participants can register bid.
If participant which did not was on first stage try create bid, he will catch error

.. include:: tutorial/stage2/EU/try-register-bidder.http
   :code:

Get error, now participant from first stage try

.. include:: tutorial/stage2/EU/register-bidder.http
   :code:

and approve to pending status:

.. include:: tutorial/stage2/EU/activate-bidder.http
   :code:

Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal technical document(s):

.. include:: tutorial/stage2/EU/upload-bid-proposal.http
   :code:

Confidentiality
^^^^^^^^^^^^^^^

Documents can be either public or private:

  1. Privacy settings can be changed only for the latest version of the document.
  2. When you upload new version of the document, privacy settings are copied from the previous version.
  3. Privacy settings can be changed only during `tenderPeriod` (with `active.tendering` status).
  4. If tender has status `active.qualification` winner can upload only public documents.

Let's upload private document:

.. include:: tutorial/stage2/EU/upload-bid-private-proposal.http
   :code:

To define the document as "private" - `confidentiality` and `confidentialityRationale` fields should be set.

`confidentiality` field value can be either `buyerOnly` (document is private) or `public` (document is publicly accessible).

Content of private documents (`buyerOnly`) can be accessed only by procuring entity or by participant who uploaded them.

`confidentialityRationale` field is required only for private documents and should contain at least 30 characters.

Let's mark the document as "private":

.. include:: tutorial/stage2/EU/mark-bid-doc-private.http
   :code:

It is possible to check the uploaded documents:

.. include:: tutorial/stage2/EU/bidder-documents.http
   :code:

.. _envelopes:

Financial documents uploading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Financial documents are also a part of Bid but are located in different end-points.

In order to create and/or get financial document ``financial_documents`` end-point should be used:

.. include:: tutorial/stage2/EU/upload-bid-financial-document-proposal.http
   :code:

Get financial documents:

.. include:: tutorial/stage2/EU/bidder-financial-documents.http
   :code:


`Financial` documents will be publicly accessible after the auction.

Here is bidder proposal with all documents.

.. include:: tutorial/stage2/EU/bidder-view-financial-documents.http
   :code:

Note that financial documents are stored in `financialDocuments` attributes of :ref:`Bid`.


Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. include:: tutorial/stage2/EU/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. include:: tutorial/stage2/EU/bidder-activate-after-changing-tender.http
   :code:

Second stage EU Competitive Dialogue procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage:

.. include:: tutorial/stage2/EU/register-2nd-bidder.http
   :code:

Batch-mode bid registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register one more bid with documents using single request (batch-mode):

.. include:: tutorial/stage2/EU/register-3rd-bidder.http
   :code:


.. index:: Awarding, Qualification

Bid Qualification
-----------------

On second stage in Competitive Dialogue procedure requires bid qualification.

Let's list qualifications:


.. include:: tutorial/stage2/EU/qualifications-listing.http
   :code:

Approve first two bids through qualification objects:

.. include:: tutorial/stage2/EU/approve-qualification1.http
   :code:

.. include:: tutorial/stage2/EU/approve-qualification2.http
   :code:

We can also reject bid:

.. include:: tutorial/stage2/EU/reject-qualification3.http
   :code:

And check that qualified bids are switched to `active`:

.. include:: tutorial/stage2/EU/qualificated-bids-view.http
   :code:

Rejected bid is not shown in `bids/` listing.

We can access rejected bid by id:

.. include:: tutorial/stage2/EU/rejected-bid-view.http
   :code:

Procuring entity approves qualifications by switching to next status:

.. include:: tutorial/stage2/EU/pre-qualification-confirmation.http
   :code:

You may notice 10 day stand-still time set in `qualificationPeriod`.

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. include:: tutorial/stage2/EU/auction-url.http
   :code:

Bidders can find out their participation URLs via their bids:

.. include:: tutorial/stage2/EU/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. include:: tutorial/stage2/EU/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification commission registers its decision via the following call:

.. include:: tutorial/stage2/EU/confirm-qualification.http
   :code:

Setting  contract value
-----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value.

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. include:: tutorial/stage2/EU/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. include:: tutorial/stage2/EU/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. include:: tutorial/stage2/EU/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

Let's upload contract document:

.. include:: tutorial/stage2/EU/tender-contract-upload-document.http
    :code:

`201 Created` response code and `Location` header confirm that this document was added.

Let's see the list of contract documents:

.. include:: tutorial/stage2/EU/tender-contract-get-documents.http
    :code:

We can upload another contract document:

.. include:: tutorial/stage2/EU/tender-contract-upload-second-document.http
    :code:

`201 Created` response code and `Location` header confirm that the second document was uploaded.

By default, document language is Ukrainian. You can can change it and set another language for the document
by assigning appropriate language code to the `language` field (available options: ``uk``, ``en``, ``ru``).
You can also set document's title (e.g. `title_en`) and description (e.g. `description_en`) fields.
See :ref:`Document` data structure for details.

.. include:: tutorial/stage2/EU/tender-contract-patch-document.http
    :code:

Let's see the list of all added contract documents:

.. include:: tutorial/stage2/EU/tender-contract-get-documents-again.http
    :code:

Let's view separate contract document:

.. include:: tutorial/stage2/EU/tender-contract-get.http
    :code:
