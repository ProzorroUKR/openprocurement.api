.. _tutorial_stage2UA:


If on first stage you set ``procurementMethodType`` to ``CompetitiveDialogueUA``
then on second stage you have tender witch similar to Open UA procedure

Modifying tender
----------------


You can modify only ``tenderPeriod.endDate`` and ``deliveryDate`` for ``items``. Another changes will not be saved.
Let's update tender by supplementing it with all other essential properties:

.. include:: tutorial/stage2/UA/patch-tender-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: tutorial/stage2/UA/tender-listing-after-patch.http
   :code:


Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API.

.. include:: tutorial/stage2/UA/update-tender-after-enqiery.http
   :code:

That is why tenderPeriod has to be extended by 7 days.

.. include:: tutorial/stage2/UA/update-tender-after-enqiery-with-update-periods.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/stage2/UA/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/stage2/UA/tender-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: tutorial/stage2/UA/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/stage2/UA/tender-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/stage2/UA/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/stage2/UA/tender-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

Enquiries
---------

When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions.
Ask question can only participants which were approved on first stage, someone else try ask, he catch error:

.. include:: tutorial/stage2/UA/ask-question-bad-participant.http
   :code:


.. include:: tutorial/stage2/UA/ask-question.http
   :code:

Procuring entity can answer them:

.. include:: tutorial/stage2/UA/answer-question.http
   :code:

One can retrieve either questions list:

.. include:: tutorial/stage2/UA/list-question.http
   :code:

or individual answer:

.. include:: tutorial/stage2/UA/get-answer.http
   :code:


Enquiries can be made only during ``Tender.enqueryPeriod``

.. include:: tutorial/stage2/UA/ask-question-after-enquiry-period.http
   :code:


.. index:: Bidding

Registering bid
---------------

Tender status ``active.tendering`` allows registration of bids.

Like with question only approved participants can register bid.
First participant witch didn't was on first stage try create bid.

.. include:: tutorial/stage2/UA/try-register-bidder.http
   :code:

Bidder can register a bid with draft status:

.. include:: tutorial/stage2/UA/register-bidder.http
   :code:

And activate a bid:

.. include:: tutorial/stage2/UA/activate-bidder.http
   :code:

Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal document(s):

.. include:: tutorial/stage2/UA/upload-bid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. include:: tutorial/stage2/UA/bidder-documents.http
   :code:

Bid invalidation
~~~~~~~~~~~~~~~~

If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified:

.. include:: tutorial/stage2/UA/bidder-after-changing-tender.http
   :code:

Bid confirmation
~~~~~~~~~~~~~~~~

Bidder should confirm bid proposal:

.. include:: tutorial/stage2/UA/bidder-activate-after-changing-tender.http
   :code:


Second stage Competitive Dialogue UA procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage.

Batch-mode bid registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register one more bid with documents using single request (batch-mode):

.. include:: tutorial/stage2/UA/register-2nd-bidder.http
   :code:


.. index:: Awarding, Qualification

Auction
-------

After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`:

.. include:: tutorial/stage2/UA/auction-url.http
   :code:

Bidders can find out their participation URLs via their bids:

.. include:: tutorial/stage2/UA/bidder-participation-url.http
   :code:

See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants:

.. include:: tutorial/stage2/UA/bidder2-participation-url.http
   :code:

Confirming qualification
------------------------

Qualification commission registers its decision via the following call:

.. include:: tutorial/stage2/UA/confirm-qualification.http
   :code:

Setting contract value
----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value.

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. include:: tutorial/stage2/UA/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. include:: tutorial/stage2/UA/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. include:: tutorial/stage2/UA/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

You can upload contract documents for the second stage Competitive Dialogue procedure.

Let's upload contract document:

.. include:: tutorial/stage2/UA/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that this document was added.

Let's view the uploaded contract document:

.. include:: tutorial/stage2/UA/tender-contract-get.http
   :code: