.. _tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/tenders` endpoint:

.. include:: http/tutorial/tender-listing.http
   :code:

Just invoking it reveals empty set.

Now let's attempt creating some tender:

.. include:: http/tutorial/tender-post-attempt.http
   :code:

Error states that the only accepted Content-Type is `application/json`.

Let's satisfy the Content-type requirement:

.. include:: http/tutorial/tender-post-attempt-json.http
   :code:

Error states that no `data` has been found in JSON body.


.. index:: Tender

Creating tender
---------------

Let's create tender with the minimal (only required) data set:

.. include:: http/tutorial/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified. Pay attention to the `procurementMethodType`. Note that tender is
created with `active.enquiries` status.

Let's access the URL of the created object (the `Location` header of the response):

.. include:: http/tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

Let's see what listing of tenders reveals us:

.. include:: http/tutorial/initial-tender-listing.http
   :code:

We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.

The previous tender contained only required fields. Let's try creating tender with more data
(tender has status `created`):

.. include:: http/tutorial/create-tender-procuringEntity.http
   :code:

And again we have `201 Created` response code, `Location` header and body with extra `id`, `tenderID`, and `dateModified` properties.

Let's check what tender registry contains:

.. include:: http/tutorial/tender-listing-after-procuringEntity.http
   :code:

And indeed we have 2 tenders now.

We can create tender with optional `funders` field:

.. include:: http/tutorial/create-tender-funders.http
   :code:


Modifying tender
----------------

Let's update tender by supplementing it with all other essential properties:

.. include:: http/tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: http/tutorial/tender-listing-after-patch.http
   :code:

Procuring entity can set bid guarantee:

.. include:: http/tutorial/set-bid-guarantee.http
   :code:

Also we can modify tender by adding `funders` field data:

.. include:: http/tutorial/patch-tender-funders.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. include:: http/tutorial/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: http/tutorial/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: http/tutorial/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: http/tutorial/tender-documents-2.http
   :code:

Let’s add new `documentType` field with `technicalSpecifications` parameter to the previously uploaded document:

.. include:: http/tutorial/tender-document-add-documentType.http
   :code:

Success! Response code is `200 OK` and it confirms that `documentType` field with `technicalSpecifications` parameter was added .

Now let’s try to modify any field in our document. For example, `description`:

.. include:: http/tutorial/tender-document-edit-docType-desc.http
   :code:

`200 OK` response was returned. The description was modified successfully.

In case we made an error, we can reupload the document over the older version:

.. include:: http/tutorial/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: http/tutorial/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender is in `active.enquiry` status, interested parties can ask questions:

.. include:: http/tutorial/ask-question.http
   :code:

Procuring entity can answer them:

.. include:: http/tutorial/answer-question.http
   :code:

And one can retrieve the questions list:

.. include:: http/tutorial/list-question.http
   :code:

And individual answer:

.. include:: http/tutorial/get-answer.http
   :code:


.. index:: Bidding

Registering bid
---------------

Step-by-step registration
~~~~~~~~~~~~~~~~~~~~~~~~~

When ``Tender.tenderingPeriod.startDate`` comes, Tender switches to `active.tendering` status that allows registration of bids.

Bidder can register a bid in `draft` status:

.. include:: http/tutorial/register-bidder.http
   :code:

And activate a bid:

.. include:: http/tutorial/activate-bidder.http
   :code:

And upload proposal document:

.. include:: http/tutorial/upload-bid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. include:: http/tutorial/bidder-documents.http
   :code:

Batch-mode registration
~~~~~~~~~~~~~~~~~~~~~~~

Register bid with documents using one request:

.. include:: http/tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. include:: http/tutorial/auction-url.http
   :code:

And bidders can find out their participation URLs via their bids:

.. include:: http/tutorial/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. include:: http/tutorial/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification comission registers its decision via the following call:

.. include:: http/tutorial/confirm-qualification.http
   :code:

.. _SettingContractValue:

Setting contract value
----------------------

Let's see the created contract with next request:

.. include:: http/tutorial/tender-contract-get-contract-value.http
   :code:


By default contract value `amount` and `amountNet` is set based on the award value `amount`, but there is a possibility to set custom contract value.

You can update value `amount` and `amountNet` following next rules:

+-------------------------+------------------------------------------------------------------------+
| `valueAddedTaxIncluded` |                                                                        |
+------------+------------+                              `Validation`                              +
| `contract` |   `award`  |                                                                        |
+------------+------------+------------------------------------------------------------------------+
|            | true/false | Amount should be greater than amountNet and differ by no more than 20% |
+            +------------+------------------------------------------------------------------------+
|    true    |    true    |            Amount should be less or equal to awarded amount            |
+            +------------+------------------------------------------------------------------------+
|            |    false   |           AmountNet should be less or equal to awarded amount          |
+------------+------------+------------------------------------------------------------------------+
|            | true/false |                  Amount and amountNet should be equal                  |
+    false   +------------+------------------------------------------------------------------------+
|            | true/false |            Amount should be less or equal to awarded amount            |
+------------+------------+------------------------------------------------------------------------+

Let's set contract contract value with next request:

.. include:: http/tutorial/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. include:: http/tutorial/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. include:: http/tutorial/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

You can upload contract documents. Let's upload contract document:

.. include:: http/tutorial/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm document was added.

Let's see the list of contract documents:

.. include:: http/tutorial/tender-contract-get-documents.http
   :code:

We can add another contract document:

.. include:: http/tutorial/tender-contract-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm second document was uploaded.

Let's see the list of all added contract documents:

.. include:: http/tutorial/tender-contract-get-documents-again.http
   :code:

Contract signing flow
---------------------

Checking if contract has the `pending` status:

.. note::
   To identify a winner supplier we need to find a bid which owner won an auction.
   Bid and award should be in the status `active`. 

.. include:: http/tutorial/get-tender-contracts.http
   :code:

Changing a contract status to `pending.winner-signing` by the tender owner:

.. include:: http/tutorial/change-contract-status-to-pending-winner-signing-by-owner.http
   :code:

Uploading a sign document to the contract document by supplier:

.. include:: http/tutorial/tender-contract-upload-sign-file-by-supplier.http
   :code:

Changing a contract status to `pending` by supplier:

.. include:: http/tutorial/tutorial/change-contract-status-to-pending-by-supplier.http
   :code:

Uploading a sign document to the contract document by tender owner:

.. include:: http/tutorial/tender-contract-upload-sign-file-by-owner.http
   :code:

Set contract signature date
---------------------------

There is a possibility to set custom contract signature date.
If the date is not set it will be generated on contract registration.

.. include:: http/tutorial/tender-contract-sign-date.http
   :code:

Contract registration
---------------------

.. include:: http/tutorial/tender-contract-sign.http
   :code:

Cancelling tender
-----------------

Tender creator can cancel tender anytime (except when tender has terminal status e.g. `usuccesfull`, `canceled`, `complete`).

The following steps should be applied:

1. Prepare cancellation request
2. Fill it with the protocol describing the cancellation reasons
3. Cancel the tender with the reasons prepared.

Only the request that has been activated (3rd step above) has power to
cancel tender.  I.e.  you have to not only prepare cancellation request but
to activate it as well.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should pass `reason` and `reasonType`, `status` defaults to `draft`.

`id` is autogenerated and passed in the `Location` header of response.

.. include:: http/tutorial/prepare-cancellation.http
   :code:


Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is required. Without documents you can't update tender status.

Upload the file contents

.. include:: http/tutorial/upload-cancellation-doc.http
   :code:

Change the document description and other properties

.. include:: http/tutorial/patch-cancellation.http
   :code:

Upload new version of the document

.. include:: http/tutorial/update-cancellation-doc.http
   :code:

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: http/tutorial/active-cancellation.http
   :code:


E-Contracting 
-------------

Tender announcement stage
~~~~~~~~~~~~~~~~~~~~~~~~~

Procuring Entity registers document of `contractProforma` providing ``ID`` of template.

.. include:: http/tutorial/upload-proforma-with-templateId.http
   :code:

Afterwards system automatically (with the help of auxiliary component tempalte registry bot) extracts template document from e-Contracting template registry and generates following documents based on data extracted from template:

* `contractTemplate` - contract template document;
* `contractSchema` - document with required contract data schema for template; 
* `contractForm` - document with recommended JSON form. 


.. note:: Documents are linked with `contractProforma` by new reference type ``documentOf`` attribute equal to ``document`` and ``relatedItem`` equal to corresponding `contractProforma` document ``id``.


Let's review above mentioned documents in tender:

.. include:: http/tutorial/tender-documents-after-rg-bot.http
   :code:

Within **tenderPeriod** marketplace of Contracting Authority performs following steps:

    * Obtains documents of type `contractForm` and `contractSchema` for data collection; 
    * Acquire data about Contracting Authority according to `contractSchema` with ``role`` equal to ``buyer``; 
    * Uploads JSON document with `contractData` type with acquired data linked with `contractProforma` by providing `documentOf` attribute equal to document and `relatedItem` equal to corresponding `contractProforma` document `id`. 

Document is uploaded into **tender documents** collection;

.. include:: http/tutorial/upload-owner-contract-data.http
   :code:

Afterwards system automatically (with the help of auxiliary component renderer bot):

    * Supplements `contractData` with information about purchased product from procedure;
    * Generates initial **PDF/A file** of `contractProforma` with information about Contracting Authority and purchased product;
    * Updates tender with new version of document `contractProforma`.

.. include:: http/tutorial/get-tender-documents-after-rbot.http
   :code:

Bid submission stage
~~~~~~~~~~~~~~~~~~~~

At the bid submission stage, marketplace of Economic Operator performs following steps:

    * Obtain documents of type `contractForm` and `contractSchema` for data collection;
    * Acquire data about Economic Operator according to `contractSchema` with ``role`` equal to ``supplier``;
    * **(Optional)** Generates `contractData` document and **PDF/A file** of contract as if Economic Operator awarded as a `winner`, available for `preview`;
    * Uploads JSON document with `contractData` type with acquired data linked with `contractProforma` by providing `documentOf` attribute equal to document and `relatedItem` equal to corresponding `contractProforma` document `id`.
    
Document is uploaded into **supplier bid documents** collection;
    
.. include:: http/tutorial/upload-bidder-contract-data.http
   :code:

Contract signing stage
~~~~~~~~~~~~~~~~~~~~~~

At the beginning of the contracting process auxiliary component rBot (renderer) generates a JSON `contractData` document based on aggregated data from various procedure objects, such as: **Plan, Tender, Bid, Award** and **Contract** and forms **PDF/A** version of contract based on this file.

.. include:: http/tutorial/tender-contract-with-generated-documents.http
   :code:

.. note:: Process data related to **Plan, Tender, Award** and **Bid** at the time of contract generation are complete and can not be modified. 
   
In case of errors in aggregated `contractData` (from tender announcement or bid submission stages), Procuring Entity can upload updates for `contractData` to `contract` document until activation of the contract.

To do this marketplace of Contracting Authority performs following steps:

    * Obtains documents of type `contractForm` and `contractSchema` for data collection; 
    * Updates data about Contracting Authority and/or Economic Operator according to `contractSchema` with ``role`` equal to ``buyerCorrigenda``; 
    * Uploads JSON document with `contractData` type with acquired data linked with `contractProforma` by providing `documentOf` attribute equal to document and `relatedItem` equal to corresponding `contractProforma` document `id`. 
   
.. include:: http/tutorial/tender-contract-fix-contract-data-document.http
   :code:

Let's review updated document in tender:
   
.. include:: http/tutorial/tender-contract-get-documents.http
   :code:
