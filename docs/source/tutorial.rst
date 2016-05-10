.. _tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/contracts` endpoint:

.. include:: tutorial/contracts-listing-0.http
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

Contract in the tender system

.. include:: tutorial/example_contract.http
   :code:

*Contract id is the same in both tender and contract system.*

Let's access the URL of the created object:

.. include:: tutorial/contract-view.http
   :code:

Note that contract is created in ``draft`` status.

Getting access
--------------

In order to get rights for future contract editing, you need to use this view ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}`` with the API key of the eMall (broker), where tender was generated.

In the ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}``: 

* ``id`` stands for contract id, 

* ``tender_token`` is tender's token (is used for contract token generation).

Response will contain ``access.token`` for the contract that can be used for further contract modification.

.. include:: tutorial/contract-credentials.http
   :code:

Contracts in ``draft`` status are not visible in listings.

.. include:: tutorial/contracts-listing-1.http
   :code:

Contract should be ``active`` to become available in listings.

Contract activation
-------------------
Before any contract modification you have to activate contract.

.. include:: tutorial/contract-activation.http
   :code:

Let's see what listing of contracts reveals us:

.. include:: tutorial/contracts-listing-2.http
   :code:

We do see the internal `id` of a contract (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/contracts/`) and its `dateModified` datestamp.


Modifying contract
------------------

Let's update contract by supplementing it with all other essential properties.

.. include:: tutorial/contracts-patch.http
   :code:

We see the added properties have merged with existing contract data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Fields that can be modified: `title`, `description`, `status`, `value.amount`, `period`, `items`.

Add item:

.. include:: tutorial/add-contract-item.http
   :code:

Update item:

.. include:: tutorial/update-contract-item.http
   :code:

Delete item:

.. include:: tutorial/delete-contract-item.http
   :code:


Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created contract. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/upload-contract-document.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. include:: tutorial/contract-documents.http
   :code:

And again we can confirm that there are two documents uploaded.

.. include:: tutorial/upload-contract-document-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/upload-contract-document-3.http
   :code:

And we can see that it is overriding the original version:

.. include:: tutorial/get-contract-document-3.http
   :code:


.. index:: Enquiries, Question, Answer

Completing contract
-------------------

Contract can be completed by switching to ``terminated`` status.

.. include:: tutorial/contract-termination.http
   :code:

Any future modification to the contract are not allowed.
