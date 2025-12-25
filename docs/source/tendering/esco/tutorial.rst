.. _esco_tutorial:

Tutorial
========

.. index:: Tender

Configuration
-------------

The set of possible configuration values:

.. csv-table::
   :file: csv/config.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

Allowed `procuringEntity.kind` values
-------------------------------------

.. csv-table::
   :file: csv/kind.csv
   :header-rows: 1

Creating tender
---------------

Let's provide the data attribute in the submitted body :

.. http:example:: tutorial/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified.  Note that tender is created with `draft` status.

The peculiarity of the ESCO procedure is that ``procurementMethodType`` is ``esco``.
Also,  new fields ``NBUdiscountRate``, ``minimalStepPercentage``, ``fundingKind``, ``yearlyPaymentsPercentageRange``  were added to tender object.

There is also no opportunity to set up ``enquiryPeriod``, it will be assigned automatically.


Let's access the URL of the created object (the `Location` header of the response):

.. http:example:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

Let's see what listing of tenders reveals us:

.. http:example:: tutorial/tender-listing-no-auth.http
   :code:

We don't see internal `id` of tender, because tender appears in the listing from `active.tendering` status.

Tender can contain several different lots. We can add lot using the following way:

.. http:example:: tutorial/tender-add-lot.http
   :code:

Also you will need to update data about item's related lots:

.. http:example:: tutorial/tender-add-relatedLot-to-item.http
   :code:

Tender activating
-----------------

At first we needed to add EXCLUSION criteria to our tender(:ref:`About criteria you can read here<criteria_operation>`).

.. http:example:: tutorial/add-exclusion-criteria.http
   :code:

Before activating tender it is required to add sign document to tender.
If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/notice-document-required.http
   :code:

Sign document should have `documentType: notice` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/add-notice-document.http
   :code:

After adding needed criteria and sign document we can activate our tender, so let's do that:

.. http:example:: tutorial/tender-activating.http
   :code:

Let's see what listing of tenders reveals us:

.. http:example:: tutorial/active-tender-listing-no-auth.http
   :code:

Now We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.

Modifying tender
----------------

Let's update tender by supplementing it with all other essential properties:

.. http:example:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: tutorial/tender-listing-after-patch.http
   :code:

Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. http:example:: tutorial/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. http:example:: tutorial/update-tender-after-enqiery-with-update-periods.http
   :code:

Procuring entity can set bid guarantee:

.. http:example:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. http:example:: tutorial/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: tutorial/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. http:example:: tutorial/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. http:example:: tutorial/tender-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. http:example:: tutorial/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: tutorial/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enquiryPeriod.endDate``  hasn't come yet, interested parties can ask questions:

.. http:example:: tutorial/ask-question.http
   :code:

Procuring entity can answer them:

.. http:example:: tutorial/answer-question.http
   :code:

One can retrieve either questions list:

.. http:example:: tutorial/list-question.http
   :code:

or individual answer:

.. http:example:: tutorial/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enquiryPeriod``

.. http:example:: tutorial/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Bid registration
~~~~~~~~~~~~~~~~

Tender status ``active.tendering`` allows registration of bids.

Bidder can register a bid for lot №1 with `draft` status:

.. http:example:: tutorial/register-bidder.http
   :code:

And append responses for criteria requirements:

.. http:example:: tutorial/add-requirement-responses-to-bidder.http
   :code:

Then bidder should approve bid with pending status. If `tenderers.identifier.scheme = 'UA-EDR'` it is required to add sign document to bid.
If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/activate-bidder-without-proposal.http
   :code:

Sign document should have `documentType: proposal` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/upload-bid-proposal.http
   :code:

Let's try to activate bid one more time:

.. http:example:: tutorial/activate-bidder.http
   :code:

If we patched some fields in pending bid, then bid becomes `invalid` and should be signed one more time:

.. http:example:: tutorial/patch-pending-bid.http
   :code:

If we try to activate bidder the new sign will be needed:

.. http:example:: tutorial/activate-bidder-without-sign.http
   :code:

Confidentiality for bids
^^^^^^^^^^^^^^^^^^^^^^^^

Documents can be either public or private:

  1. Privacy settings can be changed only for the latest version of the document.
  2. When you upload new version of the document, privacy settings are copied from the previous version.
  3. Privacy settings can be changed only during `tenderPeriod` (with `active.tendering` status).
  4. If tender has status `active.qualification` winner can upload only public documents.

Let's upload private document:

.. http:example:: tutorial/upload-bid-private-proposal.http
   :code:

To define the document as "private" - `confidentiality` and `confidentialityRationale` fields should be set.

`confidentiality` field value can be either `buyerOnly` (document is private) or `public` (document is publicly accessible).

Content of private documents (`buyerOnly`) can be accessed only by procuring entity or by participant who uploaded them.

`confidentialityRationale` field is required only for private documents and should contain at least 30 characters.

Let's mark the document as "private":

.. http:example:: tutorial/mark-bid-doc-private.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: tutorial/bidder-documents.http
   :code:

.. _esco_envelopes:

Financial, eligibility and qualification documents uploading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Financial, eligibility and qualification documents are also a part of Bid but are located in different end-points.

In order to create and/or get financial document ``financial_documents`` end-point should be used:

.. http:example:: tutorial/upload-bid-financial-document-proposal.http
   :code:

Get financial documents:

.. http:example:: tutorial/bidder-financial-documents.http
   :code:

In order to create and/or get eligibility document ``eligibility_documents`` end-point should be used:

.. http:example:: tutorial/upload-bid-eligibility-document-proposal.http
   :code:

In order to create and/or get qualification document ``qualification_documents`` end-point should be used:

.. http:example:: tutorial/upload-bid-qualification-document-proposal.http
   :code:


`Financial` and `qualification` documents will be publicly accessible after the auction.
`Eligibility` documents will become publicly accessible starting from tender pre-qualification period.

Here is bidder proposal with all documents.

.. http:example:: tutorial/bidder-view-financial-documents.http
   :code:

Note that financial, eligibility, and qualification documents are stored in `financialDocuments`, `eligibilityDocuments`, and `qualificationDocuments` attributes of :ref:`Bid`.


Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. http:example:: tutorial/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. http:example:: tutorial/bidder-activate-after-changing-tender.http
   :code:

ESCO procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage. So let's create second bid:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:

Batch-mode bid registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register one more bid with documents using single request (batch-mode):

.. http:example:: tutorial/register-3rd-bidder.http
   :code:


.. index:: Awarding, Qualification

Bid Qualification
-----------------

ESCO procedure requires bid qualification.

Let's list qualifications:


.. http:example:: tutorial/qualifications-listing.http
   :code:

Approve first two bids through qualification objects:

.. http:example:: tutorial/approve-qualification1.http
   :code:

.. http:example:: tutorial/approve-qualification2.http
   :code:

We can also reject bid:

.. http:example:: tutorial/reject-qualification3.http
   :code:

And check that qualified bids are switched to `active`:

.. http:example:: tutorial/qualificated-bids-view.http
   :code:

Rejected bid is not shown in `bids/` listing.

We can access rejected bid by id:

.. http:example:: tutorial/rejected-bid-view.http
   :code:

Procuring entity approves qualifications by switching to next status.

Before approving qualifications it is required to add sign document to tender. Sign doc should be added generally for tender if there is no lots. If there is no sign document during approving qualification, we will see an error:

.. http:example:: tutorial/pre-qualification-sign-doc-is-required.http
   :code:

Sign document should have `documentType: evaluationReports` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/upload-evaluation-reports-doc.http
   :code:

Let's approve qualifications one more time:

.. http:example:: tutorial/pre-qualification-confirmation.http
   :code:

You may notice 10 day stand-still time set in `qualificationPeriod`.

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. http:example:: tutorial/auction-url.http
   :code:

Bidders can find out their participation URLs via their bids:

.. http:example:: tutorial/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. http:example:: tutorial/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification comission can set award to `active` or `unsuccessful` status.

There are validations before registering qualification decision:

* `eligible: True` and `qualified: True` - for setting award from `pending` to `active`

* `eligible: False` and `qualified: True` OR `eligible: True` and `qualified: False` OR `eligible: False` and `qualified: False` - for setting award from `pending` to `unsuccessful`

Let's try to set `unsuccessful` status for `qualified` and `eligible` award and we will see an error:

.. http:example:: tutorial/unsuccessful-qualified-award.http
   :code:

Let's try to set `active` status for `non-qualified` or `non-eligible` award and we will see an error:

.. http:example:: tutorial/activate-non-qualified-award.http
   :code:

Before making decision it is required to add sign document to award.
If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/award-notice-document-required.http
   :code:

The same logic for `unsuccessful` status:

.. http:example:: tutorial/award-unsuccessful-notice-document-required.http
   :code:

Sign document should have `documentType: notice` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/award-add-notice-document.http
   :code:

Qualification commission registers its decision via the following call:

.. http:example:: tutorial/confirm-qualification.http
   :code:


.. index:: Setting Contract

Setting Contract
----------------

EContracting is unavailable for `esco` procedures.

In regular contacting the contract will be created in tender system first. Contract must be activated in by changing status to `active`.

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

.. http:example:: tutorial/prepare-cancellation.http
   :code:

You can change ``reasonType`` value to any of the above.

.. http:example:: tutorial/update-cancellation-reasonType.http
   :code:

Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is required. Without documents you can't update tender status.

Upload the file contents

.. http:example:: tutorial/upload-cancellation-doc.http
   :code:

Change the document description and other properties


.. http:example:: tutorial/patch-cancellation.http
   :code:

Upload new version of the document


.. http:example:: tutorial/update-cancellation-doc.http
   :code:

Passing Complaint Period
~~~~~~~~~~~~~~~~~~~~~~~~

For activate complaint period, you need to update cancellation from `draft` to `pending`.

.. http:example:: tutorial/pending-cancellation.http
   :code:

When cancellation in `pending` status the tender owner is prohibited from all actions on the tender.

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if the complaint period(duration 10 days) is over and there were no complaints or
all complaints are canceled, then cancellation will automatically update status to `active`.

