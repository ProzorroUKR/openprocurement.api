.. _cfaua_tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/tenders` endpoint:

.. http:example:: tutorial/tender-listing.http
    :code:

Just invoking it reveals empty set.

Now let's attempt creating some tender:

.. http:example:: tutorial/tender-post-attempt.http
   :code:

Error states that the only accepted Content-Type is `application/json`.

Let's satisfy the Content-type requirement:

.. http:example:: tutorial/tender-post-attempt-json.http
   :code:

Error states that no `data` has been found in JSON body.


.. index:: Tender

.. ПРЕЦЕДЕНТ Т1. Опублікувати оголошення

Creating tender
---------------

Let's create tender with the minimal (only required) data set:

.. http:example:: tutorial/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified. Pay attention to the `procurementMethodType`. Note that tender is
created with `draft` status.

Let's access the URL of the created object (the `Location` header of the response):

The peculiarity of the Close FrameworkAgreement UA procedure is that ``procurementMethodType`` was changed from
``belowThreshold`` to ``closeFrameworkAgreementUA``.
Also there is no opportunity to set up ``enquiryPeriod``, it will be assigned automatically.

.. http:example:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

Let's see what listing of tenders reveals us:

.. http:example:: tutorial/initial-tender-listing.http
   :code:

We don't see internal `id` of tender, because tender appears in the listing from `active.enquiries` status.

You can add additional :ref:`ContactPoint` and set several :ref:`Item`. Also you can create tender with :ref:`Feature` (`https://prozorro-api-docs.readthedocs.io/uk/frameworkagreement/basic-actions/meat.html?highlight=features#announcing-meat`).

Tender activating
-----------------

At first we needed to add EXCLUSION criteria to our tender(:ref:`About criteria you can read here<criteria_operation>`).

.. http:example:: tutorial/add-exclusion-criteria.http
   :code:

After adding needed criteria we can activate our tender, so let's do that:

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

Procuring entity can set bid guarantee:

.. http:example:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

You can modify the following fields on this step: ``agreementDuration``, :ref:`item`, ``maxAwardsCount``, :ref:`ProcuringEntity`, ``tenderPeriod``, ``title``, ``title_ru``, ``title_en``,
``description``, ``description_ru``, ``description_en``, ``eligibilityCriteria``, ``procurementMethodRationale``, ``guarantee``, :ref:`feature`, :ref:`document`, :ref:`lot`.


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


.. ПРЕЦЕДЕНТ Т5. Задати питання

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``
hasn't come yet, interested parties can ask questions:

.. http:example:: tutorial/ask-question.http
   :code:

Procuring entity can answer them:

.. http:example:: tutorial/answer-question.http
   :code:

And one can retrieve the questions list:

.. http:example:: tutorial/list-question.http
   :code:

And individual answer:

.. http:example:: tutorial/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. http:example:: tutorial/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

.. ПРЕЦЕДЕНТ Т3. Подати пропозицію
.. ПРЕЦЕДЕНТ Т4. Внести зміну в пропозицію

Registering bid
---------------

Step-by-step registration
~~~~~~~~~~~~~~~~~~~~~~~~~

Tender status ``active.tendering`` allows registration of bids.

Bidder can register a bid in `draft` status:

.. http:example:: tutorial/register-bidder.http
   :code:

And append responses for criteria requirements:

.. http:example:: tutorial/add-requirement-responses-to-bidder.http
   :code:

And activate a bid:

.. http:example:: tutorial/activate-bidder.http
   :code:

Bidder can also submit bid with non-price criteria - :ref:`parameter` (`https://prozorro-api-docs.readthedocs.io/uk/frameworkagreement/basic-actions/meat.html?highlight=features#bidding-in-meat`).

Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal technical document(s):

.. http:example:: tutorial/upload-bid-proposal.http
   :code:

Confidentiality
^^^^^^^^^^^^^^^

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

.. _envelopes:

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

In case we made an error, we can reupload the document over the older version:

.. http:example:: tutorial/upload-bid-qualification-document-proposal-updated.http
   :code:


`Financial` and `qualification` documents will be publicly accessible after the auction.
`Eligibility` documents will become publicly accessible starting from tender pre-qualification period.

Here is bidder proposal with all documents.

.. http:example:: tutorial/bidder-view-financial-documents.http
   :code:

Note that financial, eligibility, and qualification documents are stored in `financialDocuments`,
`eligibilityDocuments`, and `qualificationDocuments` attributes of :ref:`Bid`.


Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``.
Bid proposal will look the following way after tender has been modified:

.. http:example:: tutorial/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. http:example:: tutorial/bidder-activate-after-changing-tender.http
   :code:

Bidder can change his bid after activating it. He can change value:amount (:ref:`value`). Also he can update :ref:`parameter`, subContractors, :ref:`document`.

Close FrameworkAgreement UA procedure demands at least three bidders, so there should be at least three bid proposals
registered to move to auction stage:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:


Batch-mode registration
~~~~~~~~~~~~~~~~~~~~~~~

Register bid with documents using one request:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification


.. ПРЕЦЕДЕНТ Т10. Провести прекваліфікацію

Bid Qualification
-----------------

Close FrameworkAgreement UA procedure requires bid qualification.

Let's list qualifications:


.. http:example:: tutorial/qualifications-listing.http
   :code:

Approve three bids through qualification objects:

.. http:example:: tutorial/approve-qualification1.http
   :code:

.. http:example:: tutorial/approve-qualification2.http
   :code:

.. http:example:: tutorial/approve-qualification4.http
   :code:

We can also reject bid:

.. http:example:: tutorial/reject-qualification3.http
   :code:

To reject bid, Procuring entity should specify reason of rejection in ``description`` field.

And check that qualified bids are switched to `active`:

.. http:example:: tutorial/qualificated-bids-view.http
   :code:

Rejected bid is not shown in `bids/` listing.

We can access rejected bid by id:

.. http:example:: tutorial/rejected-bid-view.http
   :code:

Procuring entity approves qualifications by switching to next status:

.. http:example:: tutorial/pre-qualification-confirmation.http
   :code:

Procuring entity may change ``status`` of Bid on opposite during `active.prequalification`.

You may notice 10 day stand-still time set in `qualificationPeriod`.

.. ПРЕЦЕДЕНТ Т11. Брати участь в аукціоні

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.lot.auctionUrl`:

.. http:example:: tutorial/auction-url.http
   :code:

And bidders can find out their participation URLs via their bids:

.. http:example:: tutorial/bidder-participation-url.http
   :code:

See the `Bid.lotValues.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. http:example:: tutorial/bidder2-participation-url.http
   :code:

.. http:example:: tutorial/bidder4-participation-url.http
   :code:

.. ПРЕЦЕДЕНТ Т12. Визначити переможців

Confirming qualification
------------------------

Qualification board receives the qualifications list

.. http:example:: tutorial/qualifications-list.http
   :code:

And registers its decisions via the following call `per award`:

.. http:example:: tutorial/confirm-qualification.http
   :code:

The board may cancel the award winner by calling
``{'data': {'status': 'cancelled'}}``

.. http:example:: tutorial/patch-award-cancelled.http
   :code:

We can see new `pending` award is generated for the same bidder.

.. http:example:: tutorial/qualifications-list2.http
   :code:

Now we can patch `pending` award to `unsuccessful`.

.. http:example:: tutorial/patch-award-unsuccessful.http
   :code:

In case of transferring award from ``unsuccessful`` to ``cancelled``, tender moves to the beginning of ``active.qualification`` status, all of the awards become ``cancelled`` and new :ref:`award` objects are creating.

So we patch `unsuccessful` award to `cancelled`.

.. http:example:: tutorial/patch-award-unsuccessful-cancelled.http
   :code:

New `pending` award is generated for each bidder.

.. http:example:: tutorial/qualifications-list3.http
   :code:

Finally we confirm all `pending` awards via the following call:

.. http:example:: tutorial/confirm-qualification2.http
   :code:

Procuring entity may specify reasons of Bidder disqualification in the ``description`` field.

Procuring entity may continue consideration of decision for some :ref:`award` if it is needed. Procuring entity should upload a document for that.

Completion of qualification is transfer procedure into `active.qualification.stand-still` status.


.. ПРЕЦЕДЕНТ Т13. Додати документи з цінами

Uploading document with unit price per item
-------------------------------------------

When tender transfers to status `active.awarded` then :ref:`Agreement` is created and the awarded participants are given 5 business days to upload the itemized price list with unit price per every 'item' 

.. http:example:: tutorial/upload-prices-document.http
   :code:

Entering prices per item by the ordering party
----------------------------------------------

The object list :ref:`Agreement` can be obtained via the following call

.. http:example:: tutorial/agreements-list.http
   :code:

Only one contract is created per each qualified award winner

The object list :ref:`Contract` to enter prices per item can be obtained by the ordering party via the following call 

.. http:example:: tutorial/agreement-contracts-list.http
   :code:

Entering unit prices is allowed only for all 'items' taken together

.. http:example:: tutorial/agreement-contract-unitprices1.http
   :code:

.. http:example:: tutorial/agreement-contract-unitprices2.http
   :code:

.. http:example:: tutorial/agreement-contract-unitprices3.http
   :code:

Also the ordering party is allowed to exclude a winner from the framework agreement by setting the contract to 
``{'data': {'status': 'unsuccessful'}}``

For a successful signing of a Framework agreement not less than 3 active contracts are needed 

A Framework agreement can be signed only when `agreement.contractPeriod.clarificationsUntil` is reached

Procuring entity may fill the information about ``agreementNumber``.


Uploading agreement documentation
---------------------------------

You can upload agreement documents. Let's upload agreement document:

.. http:example:: tutorial/tender-agreement-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that this document was added.

Let's see the list of agreement documents:

.. http:example:: tutorial/tender-agreement-get-documents.http
   :code:

We can add another agreement document:

.. http:example:: tutorial/tender-agreement-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm that the second document was uploaded.

By default, document language is Ukrainian. You can can change it and set another language for the document
by assigning appropriate language code to the `language` field (available options: ``uk``, ``en``, ``ru``).
You can also set document's title (e.g. `title_en`) and description (e.g. `description_en`) fields.
See :ref:`Document` data structure for details.

.. http:example:: tutorial/tender-agreement-patch-document.http
    :code:

Let's see the list of all added agreement documents:

.. http:example:: tutorial/tender-agreement-get-documents-again.http
   :code:

Let's view separate contract document:

.. http:example:: tutorial/tender-agreement-get.http
    :code:


Set agreement signature date
----------------------------

There is a possibility to set custom agreement signature date.
If the date is not set it will be generated on agreement registration.

.. http:example:: tutorial/tender-agreement-sign-date.http
   :code:

Agreement registration
----------------------

.. http:example:: tutorial/tender-agreement-sign.http
   :code:

Cancelling tender
-----------------

Tender creator can cancel tender anytime (except when tender in status `active.auction` or in terminal status e.g. `unsuccessful`, `canceled`, `complete`).

The following steps should be applied:

1. Prepare cancellation request
2. Fill it with the protocol describing the cancellation reasons
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

Transfer agreement to `unsuccessful`
------------------------------------

Procuring entity can patch `agreement` to  `unsuccessful`.

.. http:example:: tutorial/agreement-unsuccessful.http
   :code:

This will transfer `tender` to `unsuccessful` status.

.. http:example:: tutorial/tender-unsuccessful.http
   :code:
