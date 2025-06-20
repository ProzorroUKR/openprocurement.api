.. _tutorial:

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


Tender with inspector
---------------------

You can get info here: :ref:`inspector_tutorial`

Creating tender
---------------

Let's create tender with the minimal (only required) data set:

.. http:example:: http/tutorial/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified. Pay attention to the `procurementMethodType`. Note that tender is
created with `draft` status.

Let's access the URL of the created object (the `Location` header of the response):

.. http:example:: http/tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

Let's see what listing of tenders reveals us:

.. http:example:: http/tutorial/initial-tender-listing.http
   :code:

We don't see internal `id` of tender, because tender appears in the listing from `active.enquiries` status.

Tender can contain several different lots. We can add lot using the following way:

.. http:example:: http/tutorial/tender-add-lot.http
   :code:

Also you will need to update data about item's related lots:

.. http:example:: http/tutorial/tender-add-relatedLot-to-item.http
   :code:

Tender activating
~~~~~~~~~~~~~~~~~

Before activating tender it is required to add sign document to tender.
If there is no sign document during activation, we will see an error:

.. http:example:: http/tutorial/notice-document-required.http
   :code:

Sign document should have `documentType: notice` and `title: *.p7s`. Let's add such document:

.. http:example:: http/tutorial/add-notice-document.http
   :code:

For activating tender you should update status to ``active.enquiries``:

.. http:example:: http/tutorial/tender-activating.http
   :code:

Let's see what listing of tenders reveals us:

.. http:example:: http/tutorial/active-tender-listing-no-auth.http
   :code:

We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.


Creating second tender
----------------------

The previous tender contained only required fields. Let's try creating tender with more data
(tender has status `created`):

.. http:example:: http/tutorial/create-tender-procuringEntity.http
   :code:

And again we have `201 Created` response code, `Location` header and body with extra `id`, `tenderID`, and `dateModified` properties.

Let's check what tender registry contains:

.. http:example:: http/tutorial/tender-listing-after-procuringEntity.http
   :code:

And indeed we have 2 tenders now.

We can create tender with optional `funders` field:

.. http:example:: http/tutorial/create-tender-funders.http
   :code:


Modifying tender
----------------

Let's update tender by supplementing it with all other essential properties:

.. http:example:: http/tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properties have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: http/tutorial/tender-listing-after-patch.http
   :code:

Procuring entity can set bid guarantee:

.. http:example:: http/tutorial/set-bid-guarantee.http
   :code:

Also we can modify tender by adding `funders` field data:

.. http:example:: http/tutorial/patch-tender-funders.http
   :code:


.. index:: Document
.. _bt-documents-tutorial:

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. http:example:: http/tutorial/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: http/tutorial/tender-documents.http
   :code:


Let’s add new `documentType` field with `technicalSpecifications` parameter to the previously uploaded document:

.. http:example:: http/tutorial/tender-document-add-documentType.http
   :code:

Success! Response code is `200 OK` and it confirms that `documentType` field with `technicalSpecifications` parameter was added .


Here is the basic list of fields that can be changed for a document.

* documentOf
* language
* documentType
* title
* title_en
* description
* description_en
* format
* relatedItem


We can modify more of them:

.. http:example:: http/tutorial/tender-document-edit-docType-desc.http
   :code:

You may notice that `dateModified` field changes with every modification.


The single array element describes the uploaded document. We can upload more documents:

.. http:example:: http/tutorial/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. http:example:: http/tutorial/tender-documents-2.http
   :code:


Before we updated document details. It is also possible to change document content itself (file).
To do so, we can upload a new version of the document:

.. http:example:: http/tutorial/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: http/tutorial/tender-documents-3.http
   :code:

Please notice that `datePublished` field has also been changed.
It is connected to the document file and only changes when a new file uploaded.


It is possible to see all versions of all documents. To do this, use `?all=1` parameter.

.. http:example:: http/tutorial/tender-documents-3-all.http
   :code:

In the response you should see one version of the Notice document
and two versions of the AwardCriteria document.
Both versions have the same `id` field, but `datePublished` fields are different.
Because that's the time when files were published.

Notice, the `datePublished` and `dateModified` fields are the same.
That's because their documents details haven't been additionally changed.


Also notice, the fields that can be additionally modified like title, language, description etc.
All of them are applied to the latest version. The previous version keeps its own values.


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender is in `active.enquiry` status, interested parties can ask questions:

.. http:example:: http/tutorial/ask-question.http
   :code:

Procuring entity can answer them:

.. http:example:: http/tutorial/answer-question.http
   :code:

And one can retrieve the questions list:

.. http:example:: http/tutorial/list-question.http
   :code:

And individual answer:

.. http:example:: http/tutorial/get-answer.http
   :code:


.. index:: Bidding

Registering bid
---------------

Step-by-step registration
~~~~~~~~~~~~~~~~~~~~~~~~~

When ``Tender.tenderingPeriod.startDate`` comes, Tender switches to `active.tendering` status that allows registration of bids.

It is forbidden to patch tender in `active.tendering` status for `belowThreshold` procedure:

.. http:example:: http/tutorial/update-tender-after-enquiry.http
   :code:

Bidder can register a bid for lot №1 in `draft` status:

.. http:example:: http/tutorial/register-bidder.http
   :code:

Then bidder should approve bid with pending status. If `tenderers.identifier.scheme = 'UA-EDR'` it is required to add sign document to bid.
If there is no sign document during activation, we will see an error:

.. http:example:: http/tutorial/activate-bidder-without-proposal.http
   :code:

Sign document should have `documentType: proposal` and `title: *.p7s`. Let's add such document:

.. http:example:: http/tutorial/upload-bid-proposal.http
   :code:

Let's try to activate bid one more time:

.. http:example:: http/tutorial/activate-bidder.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: http/tutorial/bidder-documents.http
   :code:

If tender has multicurrency turned off, than there will be validation that sum of `items.unit.value` could not be more than bid value:

.. http:example:: http/tutorial/register-bidder-invalid.http
   :code:

If we patched some fields in pending bid, then bid becomes `invalid` and should be signed one more time:

.. http:example:: http/tutorial/patch-pending-bid.http
   :code:

If we try to activate bidder the new sign will be needed:

.. http:example:: http/tutorial/activate-bidder-without-sign.http
   :code:

Batch-mode registration
~~~~~~~~~~~~~~~~~~~~~~~

Register bid with documents using one request:

.. http:example:: http/tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. http:example:: http/tutorial/auction-url.http
   :code:

And bidders can find out their participation URLs via their bids:

.. http:example:: http/tutorial/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. http:example:: http/tutorial/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification comission can set award to `active` or `unsuccessful` status.

There are validations before registering qualification decision:

* `qualified: True` - for setting award from `pending` to `active`

* `qualified: False` - for setting award from `pending` to `unsuccessful`

Let's try to set `unsuccessful` status for `qualified` award and we will see an error:

.. http:example:: http/tutorial/unsuccessful-qualified-award.http
   :code:

Let's try to set `active` status for `non-qualified` award and we will see an error:

.. http:example:: http/tutorial/activate-non-qualified-award.http
   :code:

Before making decision it is required to add sign document to award.
If there is no sign document during activation, we will see an error:

.. http:example:: http/tutorial/award-notice-document-required.http
   :code:

The same logic for `unsuccessful` status:

.. http:example:: http/tutorial/award-unsuccessful-notice-document-required.http
   :code:

Sign document should have `documentType: notice` and `title: *.p7s`. Let's add such document:

.. http:example:: http/tutorial/award-add-notice-document.http
   :code:

Qualification comission registers its decision via the following call:

.. http:example:: http/tutorial/confirm-qualification.http
   :code:


.. index:: Setting Contract

Setting Contract
----------------

In EContracting the contract is created directly in contracting system.

.. note::
    Some of data will be mirrored to tender until contract will be activated for backward compatibility.

Read more about working with EContracting in contracting system in :ref:`contracting_tutorial` section.


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

.. http:example:: http/tutorial/prepare-cancellation.http
   :code:


Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is required. Without documents you can't update tender status.

Upload the file contents

.. http:example:: http/tutorial/upload-cancellation-doc.http
   :code:

Change the document description and other properties

.. http:example:: http/tutorial/patch-cancellation.http
   :code:

Upload new version of the document

.. http:example:: http/tutorial/update-cancellation-doc.http
   :code:

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: http/tutorial/create-tender-funders.http
   :code:
