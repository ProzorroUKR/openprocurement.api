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


Getting access
--------------

In order to get rights for future contract editing, you need to use this view ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}`` with the API key of the eMall (broker), where tender was generated.

In the ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}``:

* ``id`` stands for contract id,

* ``tender_token`` is tender's token (is used for contract token generation).

Response will contain ``access.token`` for the contract that can be used for further contract modification.

.. include:: tutorial/contract-credentials.http
   :code:

Let's view contracts.

.. include:: tutorial/contracts-listing-1.http
   :code:


We do see the internal `id` of a contract (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/contracts/`) and its `dateModified` datestamp.


Modifying contract
------------------

You can make changes to the contract in cases described in the 4th part of Article 36 of the Law "On the Public Procurement".

**Essential contract terms** can be modified by the submission of a new :ref:`change` object to the `Contract.changes` container.

All `changes` are processed by the endpoint `/contracts/{id}/changes`.

Submitting a change
~~~~~~~~~~~~~~~~~~~

Let's add new `change` to the contract:

.. include:: tutorial/add-contract-change.http
   :code:

Note that you can provide more than one value in ``rationaleTypes`` field.

You can view the `change`:

.. include:: tutorial/view-contract-change.http
   :code:

`Change` can be modified while it is in the ``pending`` status:

.. include:: tutorial/patch-contract-change.http
   :code:

Uploading change document
~~~~~~~~~~~~~~~~~~~~~~~~~

Document can be added only while `change` is in the ``pending`` status.

Document has to be added in two stages:

* you should upload document

.. include:: tutorial/add-contract-change-document.http
   :code:

* you should set document properties ``"documentOf": "change"`` and ``"relatedItem": "{change.id}"`` in order to bind the uploaded document to the `change`:

.. include:: tutorial/set-document-of-change.http
   :code:

Updating contract properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you can update contract properties which belong to the change.

.. include:: tutorial/contracts-patch.http
   :code:

We see the added properties have merged with existing contract data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Fields that can be modified: `title`, `description`, `status`, `value.amount`, `period`, `items`, `amountPaid.amount`, `terminationDetails`.

See examples of `items` customization below. You can:

* update item:

.. include:: tutorial/update-contract-item.http
   :code:

* delete item:

Request example for cases when contract has several items:

.. include:: tutorial/delete-contract-item.http
   :code:

Applying the change
~~~~~~~~~~~~~~~~~~~

`Change` can be applied by switching to the ``active`` status.

In order to apply ``active`` status `dateSigned` field must be set.

After this `change` can't be modified anymore.

.. include:: tutorial/apply-contract-change.http
   :code:

`dateSigned` field validation:

* for the first contract `change` date should be after `contract.dateSigned`;

* for all next `change` objects date should be after the previous `change.dateSigned`.

You can view all changes:

.. include:: tutorial/view-all-contract-changes.http
   :code:

All changes are also listed on the contract view.

.. include:: tutorial/view-contract.http
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

Before contract can be completed ``amountPaid`` field value should be set (regardless whether the contract was successful or unsuccessful).
Contract can be completed by switching to ``terminated`` status.
Let's perform these actions in single request:

.. include:: tutorial/contract-termination.http
   :code:

Note that you can set/change only ``amountPaid.amount`` value. ``amountPaid.currency`` and ``amountPaid.valueAddedTaxIncluded`` fields' values are generated from ``Contract.value`` field.

If contract is unsuccessful reasons for termination ``terminationDetails`` should be specified.

Any future modification to the contract are not allowed.
