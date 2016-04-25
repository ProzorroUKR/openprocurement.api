.. _tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/contracts` endpoint:

.. include:: tutorial/contracrts-listing.http
   :code:

Just invoking it reveals an empty set.

Contract is transferred from the tender system by an automated process.

.. index:: Contracts

Creating contract
-----------------

Let's say that we have conducted tender and it has ``complete`` status. When the tender is completed,  contract (that has been created in the tender system) is transferred to the contract system **automatically**.

*Brokers (eMalls) can't create contracts in the contract system.*

Getting contract
----------------

Let's access the URL of the created object (the `Location` header of the response):

.. include:: tutorial/blank-contract-view.http
   :code:

Let's see what listing of contracts reveals us:

.. include:: tutorial/contract-listing-no-auth.http
   :code:

We do see the internal `id` of a contract (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/contracts/`) and its `dateModified` datestamp.

*Contract id is the same in both tender and contract system.*

Modifying contract
------------------

Let's update contract by supplementing it with all other essential properties.

.. include:: tutorial/patch-items-value-periods.http
   :code:

We see the added properties have merged with existing contract data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date.

.. include:: tutorial/contract-listing-after-patch.http
   :code:

.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created contract. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/upload-contract-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/contract-documents.http
   :code:

The single array element describes the uploaded document. We can upload more documents:

.. include:: tutorial/upload-award-criteria.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/contract-documents-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/update-award-criteria.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/contract-documents-3.http
   :code:


.. index:: Enquiries, Question, Answer

