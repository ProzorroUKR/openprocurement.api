.. _cfaselection_tutorial:

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

.. http:example:: tutorial/blank-tender-view.http
   :code:

.. XXX body is empty for some reason (printf fails)

We can see the same response we got after creating tender.

We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.

The previous tender contained only required fields. Let's try creating tender with more data
(tender has status `created`):

.. http:example:: tutorial/create-tender-procuringEntity.http
   :code:

And again we have `201 Created` response code, `Location` header and body with extra `id`, `tenderID`, and `dateModified` properties.

To move forward, you need to change status of procedure to ``draft.pending``. This will let the bot to pull up 
:ref:`Agreement` and move tender to the next status. If provided information meets all the requirements, than the bot
moves procedure to ``active.enquiries`` status, else to ``draft.unsuccessful`` terminal status.

.. http:example:: tutorial/tender-switch-draft-pending.http
   :code:

Let's see, that our tender meets all the requirements, the bot pulled up :ref:`Agreement` of tender and changed status to ``active.enquiries``.

.. http:example:: tutorial/tender-in-active-enquiries.http
   :code:

Let's see what listing of tenders reveals us:

.. http:example:: tutorial/initial-tender-listing.http
   :code:

When you create a procedure (`draft` status), you can fill in the following fields:
   * in :ref:`Agreement` - `id`
   * in :ref:`Tender` - `title`, `title_en`, `description`, `description_en`, `guarantee`, `procurementMethodType`, `procuringEntity`
   * in :ref:`Lot` - `title`, `title_en`, `description`, `description_en`, `id`, `guarantee`
   * in :ref:`Item` - `description`, `quantity`, `relatedLot`, `unit`, `description_en`, `classification`, `additionalClassifications`, `deliveryAddress`, `deliveryDate`, `deliveryLocation`, `id`

The only field can be modified is :ref:`Tender`: `status`.


Modifying tender
----------------



Let's update tender by supplementing it with all other essential properties:

.. http:example:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was
updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: tutorial/tender-listing-after-patch.http
   :code:

Procuring entity can set bid guarantee:

.. http:example:: tutorial/set-bid-guarantee.http
   :code:


.. index:: Document

You may modify the following fields on this stage of procedure:
   * in :ref:`Tender` - `title`, `title_en`, `description`, `description_en`, `tenderPeriod`: `endDate`
   * in :ref:`Lot` - `title`, `description`, `title_en`, `description_en`, `minimalStep`, `amount`
   * in :ref:`Item` - `description`, `description_en`, `deliveryAddress`, `deliveryDate`, `quantity`
   * :ref:`Guarantee`

`tenderPeriod`:`endDate` should differ from tender publication date at least on three days.

You can modify the same fields on this stage of procedure in the case of multiple :ref:`Item` selected.


Uploading documentation
-----------------------

Procuring entity should only upload digital signature on this stage of procedure.

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

Let’s add new `documentType` field with `technicalSpecifications` parameter to the previously uploaded document:

.. http:example:: tutorial/tender-document-add-documentType.http
   :code:

Success! Response code is `200 OK` and it confirms that `documentType` field with `technicalSpecifications` parameter
was added .

Now let’s try to modify any field in our document. For example, `description`:

.. http:example:: tutorial/tender-document-edit-docType-desc.http
   :code:

`200 OK` response was returned. The description was modified successfully.

In case we made an error, we can reupload the document over the older version:

.. http:example:: tutorial/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: tutorial/tender-documents-3.http
   :code:


.. index:: Bidding


Registering bid
---------------

Step-by-step registration
~~~~~~~~~~~~~~~~~~~~~~~~~

When ``Tender.tenderingPeriod.startDate`` comes, Tender switches to `active.tendering` status that allows registration
of bids.

Bidder can register a bid in ``draft`` status:

You cannot submit a bid greater than ``agreement.contract.value``. Also Bidder can't submit a bid if he is not party of this Framework Agreement
(:ref:`Agreement`).


.. http:example:: tutorial/register-bidder-invalid.http
   :code:

.. http:example:: tutorial/register-bidder.http
   :code:

And activate a bid:

.. http:example:: tutorial/activate-bidder.http
   :code:

Bidder should only upload digital signature on this stage of procedure.

Upload proposal document:

.. http:example:: tutorial/upload-bid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: tutorial/bidder-documents.http
   :code:

Batch-mode registration
~~~~~~~~~~~~~~~~~~~~~~~

Register bid with documents using one request:

.. http:example:: tutorial/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. http:example:: tutorial/auction-url.http
   :code:

And bidders can find out their participation URLs via their bids:

.. http:example:: tutorial/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. http:example:: tutorial/bidder2-participation-url.http
   :code:

Listing awards
--------------

The pending award can be retrieved via request to list all available awards:

.. http:example:: tutorial/awards-get.http
   :code:

Confirming qualification
------------------------

Let's try to disqualify award by switching it's status from `pending` to `unsuccessful`.

.. http:example:: tutorial/award-qualification-unsuccessful.http
   :code:

As we can see it is impossible. Procuring entity should activate `pending` award at first and switch it to `cancelled` status then.

.. http:example:: tutorial/award-qualification-active.http
   :code:

Now cancelling `active` award.

.. http:example:: tutorial/award-qualification-cancelled.http
   :code:

We see that new `pending` award is generated for the same bidder now. So we can successfully switch this `pending` award to `unsuccessful`.

.. http:example:: tutorial/award-qualification-unsuccessful1.http
   :code:

Qualification comission registers its decision via the following call:

.. http:example:: tutorial/confirm-qualification.http
   :code:

Procuring entity should fill the information about extension of the bidder's term in the `description` field.

Setting  contract value
-----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value. 

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. http:example:: tutorial/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. http:example:: tutorial/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. http:example:: tutorial/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

You can upload contract documents. Let's upload contract document:

.. http:example:: tutorial/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm document was added.

Let's see the list of contract documents:

.. http:example:: tutorial/tender-contract-get-documents.http
   :code:

We can add another contract document:

.. http:example:: tutorial/tender-contract-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm second document was uploaded.

Let's see the list of all added contract documents:

.. http:example:: tutorial/tender-contract-get-documents-again.http
   :code:

Set contract signature date
---------------------------

There is a possibility to set custom contract signature date.
If the date is not set it will be generated on contract registration.

.. http:example:: tutorial/tender-contract-sign-date.http
   :code:

Contract registration
---------------------

.. http:example:: tutorial/tender-contract-sign.http
   :code:

To see more information about contract look at the `Contracting API interface to OpenProcurement database
<https://prozorro-api-docs.readthedocs.io/en/latest/contracting/index.html>`_.

Cancelling tender
-----------------

Tender creator can cancel tender anytime (except when tender in status `active.auction` or in terminal status e.g. `unsuccessful`, `canceled`, `complete`).

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

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: tutorial/active-cancellation.http
   :code:


It may be useful to see top requirements: `Test Cases for III level of accreditation <https://docs.google.com/spreadsheets/d/1-AT2RjbnSFAP75x6YNDvhKeN2Cy3tMlG6kb0tt6FScs/edit#gid=0>`_ and
`Test Cases for IV level of accreditation <https://docs.google.com/spreadsheets/d/1-93kcQ2EeuUU08aqPMDwMeAjnG2SGnEEh5RtjHWOlOY/edit#gid=0>`_.
