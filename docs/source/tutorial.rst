.. _tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/tenders` endpoint:

.. include:: tutorial/tender-listing.http
   :code:

Just invoking it reveals empty set.

Now let's attempt creating some tender:

.. include:: tutorial/tender-post-attempt.http
   :code:

Error states that the only accepted Content-Type is `application/json`.

Let's satisfy the Content-type requirement:

.. include:: tutorial/tender-post-attempt-json.http
   :code:

Error states that no `data` has been found in JSON body.


.. index:: Tender

Creating tender
---------------

Let's provide the data attribute in the submitted body :

.. include:: tutorial/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified.  Note that tender is created with `active.tendering` status.

The peculiarity of the Open EU procedure is that ``procurementMethodType`` was changed from ``belowThreshold`` to ``aboveThresholdEU``.
Also there is no opportunity to set up ``enquiryPeriod``, it will be assigned automatically.

Let's access the URL of the created object (the `Location` header of the response):

.. include:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

Let's see what listing of tenders reveals us:

.. include:: tutorial/tender-listing-no-auth.http
   :code:

We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.

Modifying tender
----------------

Let's update tender by supplementing it with all other essential properties:

.. include:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: tutorial/tender-listing-after-patch.http
   :code:

Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. include:: tutorial/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. include:: tutorial/update-tender-after-enqiery-with-update-periods.http
   :code:

Procuring entity can set bid guarantee:

.. include:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: tutorial/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/tender-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions:

.. include:: tutorial/ask-question.http
   :code:

Procuring entity can answer them:

.. include:: tutorial/answer-question.http
   :code:

One can retrieve either questions list:

.. include:: tutorial/list-question.http
   :code:

or individual answer:

.. include:: tutorial/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. include:: tutorial/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.

Bidder can register a bid with `draft` status:

.. include:: tutorial/register-bidder.http
   :code:
anjd approve to pending status:

.. include:: tutorial/activate-bidder.http
   :code:

Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal technical document(s):

.. include:: tutorial/upload-bid-proposal.http
   :code:

Confidentiality
^^^^^^^^^^^^^^^

Documents can be either public or private:

  1. Privacy settings can be changed only for the latest version of the document.
  2. When you upload new version of the document, privacy settings are copied from the previous version.
  3. Privacy settings can be changed only during `tenderPeriod` (with `active.tendering` status).
  4. If tender has status `active.qualification` winner can upload only public documents.

Let's upload private document:

.. include:: tutorial/upload-bid-private-proposal.http
   :code:

To define the document as "private" - `confidentiality` and `confidentialityRationale` fields should be set.

`confidentiality` field value can be either `buyerOnly` (document is private) or `public` (document is publicly accessible).

Content of private documents (`buyerOnly`) can be accessed only by procuring entity or by participant who uploaded them.

`confidentialityRationale` field is required only for private documents and should contain at least 30 characters.

Let's mark the document as "private":

.. include:: tutorial/mark-bid-doc-private.http
   :code:

It is possible to check the uploaded documents:

.. include:: tutorial/bidder-documents.http
   :code:

.. _envelopes:

Financial, eligibility and qualification documents uploading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Financial, eligibility and qualification documents are also a part of Bid but are located in different end-points.

In order to create and/or get financial document ``financial_documents`` end-point should be used:

.. include:: tutorial/upload-bid-financial-document-proposal.http
   :code:

Get financial documents:

.. include:: tutorial/bidder-financial-documents.http
   :code:

In order to create and/or get eligibility document ``eligibility_documents`` end-point should be used:

.. include:: tutorial/upload-bid-eligibility-document-proposal.http
   :code:

In order to create and/or get qualification document ``qualification_documents`` end-point should be used:

.. include:: tutorial/upload-bid-qualification-document-proposal.http
   :code:


`Financial` and `qualification` documents will be publicly accessible after the auction.
`Eligibility` documents will become publicly accessible starting from tender pre-qualification period.

Here is bidder proposal with all documents.

.. include:: tutorial/bidder-view-financial-documents.http
   :code:

Note that financial, eligibility, and qualification documents are stored in `financialDocuments`, `eligibilityDocuments`, and `qualificationDocuments` attributes of :ref:`Bid`.


Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. include:: tutorial/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. include:: tutorial/bidder-activate-after-changing-tender.http
   :code:

Open EU procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage:

.. include:: tutorial/register-2nd-bidder.http
   :code:

Register one more bid:

.. include:: tutorial/register-3rd-bidder.http
   :code:


.. index:: Awarding, Qualification

Bid Qualification
-----------------

Open EU procedure requires bid qualification.

Let's list qualifications:


.. include:: tutorial/qualifications-listing.http
   :code:

Approve first two bids through qualification objects:

.. include:: tutorial/approve-qualification1.http
   :code:

.. include:: tutorial/approve-qualification2.http
   :code:

We can also reject bid:

.. include:: tutorial/reject-qualification3.http
   :code:

And check that qualified bids are switched to `active`:

.. include:: tutorial/qualificated-bids-view.http
   :code:

Rejected bid is not shown in `bids/` listing.

We can access rejected bid by id:

.. include:: tutorial/rejected-bid-view.http
   :code:

Procuring entity approves qualifications by switching to next status:

.. include:: tutorial/pre-qualification-confirmation.http
   :code:

You may notice 10 day stand-still time set in `qualificationPeriod`.

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. include:: tutorial/auction-url.http
   :code:

Bidders can find out their participation URLs via their bids:

.. include:: tutorial/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. include:: tutorial/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification commission registers its decision via the following call:

.. include:: tutorial/confirm-qualification.http
   :code:

Setting  contract value
-----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value. 

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. include:: tutorial/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. include:: tutorial/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. include:: tutorial/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

You can upload contract documents for the OpenEU procedure.

Let's upload contract document:

.. include:: tutorial/tender-contract-upload-document.http
    :code:

`201 Created` response code and `Location` header confirm that this document was added.

Let's see the list of contract documents:

.. include:: tutorial/tender-contract-get-documents.http
    :code:

We can upload another contract document:

.. include:: tutorial/tender-contract-upload-second-document.http
    :code:

`201 Created` response code and `Location` header confirm that the second document was uploaded.

By default, document language is Ukrainian. You can can change it and set another language for the document by assigning appropriate language code to the `language` field (available options: ``uk``, ``en``, ``ru``). You can also set document's title (e.g. `title_en`) and description (e.g. `description_en`) fields. See :ref:`Document` data structure for details.

.. include:: tutorial/tender-contract-patch-document.http
    :code:

Let's see the list of all added contract documents:

.. include:: tutorial/tender-contract-get-documents-again.http
    :code:

Let's view separate contract document:

.. include:: tutorial/tender-contract-get.http
    :code:

Cancelling tender
-----------------

Tender creator can cancel tender anytime. The following steps should be applied:

1. Prepare cancellation request.
2. Fill it with the protocol describing the cancellation reasons.
3. Cancel the tender with the prepared reasons.

Only the request that has been activated (3rd step above) has power to
cancel tender.  I.e.  you have to not only prepare cancellation request but
to activate it as well.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should pass `reason`, `status` defaults to `pending`.

`id` is autogenerated and passed in the `Location` header of response.

.. include::  tutorial/prepare-cancellation.http
   :code:

There are two possible types of cancellation reason: tender was `cancelled` or `unsuccessful`. By default ``reasonType`` value is `cancelled`.

You can change ``reasonType`` value to `unsuccessful`.

.. include::  tutorial/update-cancellation-reasonType.http
   :code:

Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upload the file contents

.. include::  tutorial/upload-cancellation-doc.http
   :code:

Change the document description and other properties


.. include::  tutorial/patch-cancellation.http
   :code:

Upload new version of the document


.. include::  tutorial/update-cancellation-doc.http
   :code:

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include::  tutorial/active-cancellation.http
   :code:
