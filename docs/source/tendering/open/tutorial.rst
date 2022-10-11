.. _open_tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/tenders` endpoint:

.. include:: http/tender-listing.http
   :code:

Just invoking it reveals empty set.

Now let's attempt creating some tender:

.. include:: http/tender-post-attempt.http
   :code:

Error states that the only accepted Content-Type is `application/json`.

Let's satisfy the Content-type requirement:

.. include:: http/tender-post-attempt-json.http
   :code:

Error states that no `data` has been found in JSON body.


.. index:: Tender

Creating tender
---------------

Let's provide the data attribute in the submitted body :

.. include:: http/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified.  Note that tender is created with `draft` status.

The peculiarity of the Open procedure is that ``procurementMethodType`` was changed from ``belowThreshold`` to ``aboveThreshold``.
Also there is no opportunity to set up ``enquiryPeriod``, it will be assigned automatically.

Let's access the URL of the created object (the `Location` header of the response):

.. include:: http/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

Let's see what listing of tenders reveals us:

.. include:: http/tender-listing-no-auth.http
   :code:

We don't see internal `id` of tender, because tender appears in the listing from `active.tendering` status.

Tender can contain several different lots. We can add lot using the following way:

.. include:: http/tender-add-lot.http
   :code:

Also you will need to update data about item's related lots:

.. include:: http/tender-add-relatedLot-to-item.http
   :code:

Tender activating
-----------------

At first we needed to add EXCLUSION criteria to our tender(:ref:`About criteria you can read here<criteria_operation>`).

.. include:: http/add-exclusion-criteria.http
   :code:

After adding needed criteria we can activate our tender, so let's do that:

.. include:: http/tender-activating.http
   :code:

Let's see what listing of tenders reveals us:

.. include:: http/active-tender-listing-no-auth.http
   :code:

Now We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.

Modifying tender
----------------

Let's update tender by supplementing it with all other essential properties:

.. include:: http/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: http/tender-listing-after-patch.http
   :code:


Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. include:: http/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. include:: http/update-tender-after-enqiery-with-update-periods.http
   :code:

Procuring entity can set bid guarantee:

.. include:: http/set-bid-guarantee.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. include:: http/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: http/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: http/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: http/tender-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: http/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: http/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions:

.. include:: http/ask-question.http
   :code:

Procuring entity can answer them:

.. include:: http/answer-question.http
   :code:

One can retrieve either questions list:

.. include:: http/list-question.http
   :code:

or individual answer:

.. include:: http/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. include:: http/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.

Bidder can register a bid for lot №1:

.. include:: http/bid-lot1.http
   :code:

And append responses for criteria requirements:

.. include:: http/add-requirement-responses-to-bidder.http
   :code:

And activate a bid:

.. include:: http/activate-bidder.http
   :code:

Then bidder should upload proposal document(s):

.. include:: http/upload-bid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. include:: http/bidder-documents.http
   :code:

Bidder can register bids for all lots:

.. include:: http/bid-lot2.http
   :code:

Then bidder should upload technical and private documents of proposal.

We can update tender during ``active.tendering`` period. Bids will be invalid after updating tender. For example, let's reduce the lot price to 400.

.. include:: http/tender-invalid-all-bids.http
   :code:

Here is the bidder's proposal after tender was updated.

.. include:: http/bid-lot1-invalid-view.http
   :code:

Firstly bidder has to renew bid, even if he was placing a bid just for a lot №1.

.. include:: http/bid-lot1-update-view.http
   :code:

Then bidder has to renew bid only for a lot №1.

.. include:: http/bid-lot2-update-view.http
   :code:


.. index:: Awarding, Qualification

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. include:: http/auction-url.http
   :code:

Bidders can find out their participation URLs via their bids:

.. include:: http/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. include:: http/bidder2-participation-url.http
   :code:


Abnormally low price
--------------------

An award can contain a milestone of type ``apl`` 

.. include:: http/get-awards-list.http
   :code:


Procuring entity cannot change the status of the award before ``milestone.dueDate``

.. include:: http/fail-disqualification.http
   :code:


During this time the bidder can upload ``evidence`` documents to his bid

.. include:: http/post-evidence-document.http
   :code:



Confirming qualification
------------------------

Qualification commission registers its decision via the following call:

.. include:: http/confirm-qualification.http
   :code:

Setting contract value
----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value. 

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. include:: http/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. include:: http/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. include:: http/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

You can upload contract documents for the OpenUA procedure.

Let's upload contract document:

.. include:: http/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that this document was added.

Let's view the uploaded contract document:

.. include:: http/tender-contract-get.http
   :code:

Cancelling tender
-----------------

Tender creator can cancel tender anytime (except when tender in status `active.auction` or in terminal status e.g. `unsuccessful`, `canceled`, `complete`).

The following steps should be applied:

1. Prepare cancellation request.
2. Fill it with the protocol describing the cancellation reasons.
3. Passing complaint period(10 days)
4. Cancel the tender with the prepared reasons.

Only the request that has been activated (4th step above) has power to
cancel tender.  I.e.  you have to not only prepare cancellation request but
to activate it as well.

For cancelled cancellation you need to update cancellation status to `unsuccessful`
from `draft` or `pending`.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should pass `reason` and `reasonType`, `status` defaults to `draft`.

There are four possible types of cancellation reason - tender was `noDemand`, `unFixable`, `forceMajeure` and `expensesCut`.

`id` is autogenerated and passed in the `Location` header of response.

.. include::  http/prepare-cancellation.http
   :code:

You can change ``reasonType`` value to any of the above.

.. include::  http/update-cancellation-reasonType.http
     :code:

Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is required. Without documents you can't update tender status.

Upload the file contents

.. include::  http/upload-cancellation-doc.http
   :code:

Change the document description and other properties


.. include::  http/patch-cancellation.http
   :code:

Upload new version of the document


.. include::  http/update-cancellation-doc.http
   :code:

Passing Complaint Period
~~~~~~~~~~~~~~~~~~~~~~~~

For activate complaint period, you need to update cancellation from `draft` to `pending`.

.. include::  http/pending-cancellation.http
   :code:

When cancellation in `pending` status the tender owner is prohibited from all actions on the tender.

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if the complaint period(duration 10 days) is over and there were no complaints or
all complaints are canceled, then cancellation will automatically update status to `active`.
