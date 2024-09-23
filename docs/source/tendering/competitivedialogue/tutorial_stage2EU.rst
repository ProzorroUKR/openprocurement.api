.. _tutorial_stage2EU:

Configuration
-------------

The set of possible configuration values:

.. csv-table::
   :file: csv/config-eu-stage2.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

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

Then bidder should approve bid with pending status. If `tenderers.identifier.scheme = 'UA-EDR'` it is required to add sign document to bid.
If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/stage2/EU/activate-bidder-without-proposal.http
   :code:

Sign document should have `documentType: proposal` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/stage2/EU/upload-bid-proposal.http
   :code:

Let's try to activate bid one more time:

.. http:example:: tutorial/stage2/EU/activate-bidder.http
   :code:

If we patched some fields in pending bid, then bid becomes `invalid` and should be signed one more time:

.. http:example:: tutorial/stage2/EU/patch-pending-bid.http
   :code:

If we try to activate bidder the new sign will be needed:

.. http:example:: tutorial/stage2/EU/activate-bidder-without-sign.http
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
^^^^^^^^^^^^^^^^^

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. http:example:: tutorial/stage2/EU/bidder-after-changing-tender.http
   :code:

Bid confirmation
^^^^^^^^^^^^^^^^^

Bidder should confirm bid proposal:

.. http:example:: tutorial/stage2/EU/bidder-activate-after-changing-tender.http
   :code:

Second stage EU Competitive Dialogue procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage:

.. http:example:: tutorial/stage2/EU/register-2nd-bidder.http
   :code:

Batch-mode bid registration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Procuring entity approves qualifications by switching to next status.

Before approving qualifications it is required to add sign document to tender. Sign doc should be added generally for tender if there is no lots. If there is no sign document during approving qualification, we will see an error:

.. http:example:: tutorial/stage2/EU/pre-qualification-sign-doc-is-required.http
   :code:

Sign document should have `documentType: evaluationReports` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/stage2/EU/upload-evaluation-reports-doc.http
   :code:

Let's approve qualifications one more time:

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

Qualification comission can set award to `active` or `unsuccessful` status.

There are validations before registering qualification decision:

* `eligible: True` and `qualified: True` - for setting award from `pending` to `active`

* `eligible: False` and `qualified: True` OR `eligible: True` and `qualified: False` OR `eligible: False` and `qualified: False` - for setting award from `pending` to `unsuccessful`

Let's try to set `unsuccessful` status for `qualified` and `eligible` award and we will see an error:

.. http:example:: tutorial/stage2/EU/unsuccessful-qualified-award.http
   :code:

Let's try to set `active` status for `non-qualified` or `non-eligible` award and we will see an error:

.. http:example:: tutorial/stage2/EU/activate-non-qualified-award.http
   :code:

Before making decision it is required to add sign document to award.
If there is no sign document during activation, we will see an error:

.. http:example:: tutorial/stage2/EU/award-notice-document-required.http
   :code:

The same logic for `unsuccessful` status:

.. http:example:: tutorial/stage2/EU/award-unsuccessful-notice-document-required.http
   :code:

Sign document should have `documentType: notice` and `title: *.p7s`. Let's add such document:

.. http:example:: tutorial/stage2/EU/award-add-notice-document.http
   :code:

Qualification commission registers its decision via the following call:

.. http:example:: tutorial/stage2/EU/confirm-qualification.http
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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^

For activate complaint period, you need to update cancellation from `draft` to `pending`.

.. http:example:: tutorial/stage2/EU/pending-cancellation.http
   :code:

When cancellation in `pending` status the tender owner is prohibited from all actions on the tender.

Activating the request and cancelling tender
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

if the complaint period(duration 10 days) is over and there were no complaints or
all complaints are canceled, then cancellation will automatically update status to `active`.

.. http:example:: tutorial/stage2/EU/active-cancellation.http
   :code:
