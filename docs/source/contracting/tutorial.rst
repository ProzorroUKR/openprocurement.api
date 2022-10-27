.. _contracting_tutorial:

Tutorial
========

Exploring basic rules
---------------------

Let's try exploring the `/contracts` endpoint:

.. http:example:: http/contracts-listing-0.http
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

.. http:example:: http/example_contract.http
   :code:

*Contract id is the same in both tender and contract system.*

Let's access the URL of the created object:

.. http:example:: http/contract-view.http
   :code:


Getting access
--------------

In order to get rights for future contract editing, you need to use this view ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}`` with the API key of the eMall (broker), where tender was generated.

In the ``PATCH: /contracts/{id}/credentials?acc_token={tender_token}``:

* ``id`` stands for contract id,

* ``tender_token`` is tender's token (is used for contract token generation).

Response will contain ``access.token`` for the contract that can be used for further contract modification.

.. http:example:: http/contract-credentials.http
   :code:

Let's view contracts.

.. http:example:: http/contracts-listing-1.http
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

.. http:example:: http/add-contract-change.http
   :code:

Note that you can provide more than one value in ``rationaleTypes`` field.

You can view the `change`:

.. http:example:: http/view-contract-change.http
   :code:

`Change` can be modified while it is in the ``pending`` status:

.. http:example:: http/patch-contract-change.http
   :code:

Uploading change document
~~~~~~~~~~~~~~~~~~~~~~~~~

Document can be added only while `change` is in the ``pending`` status.

Document has to be added in two stages:

* you should upload document

.. http:example:: http/add-contract-change-document.http
   :code:

* you should set document properties ``"documentOf": "change"`` and ``"relatedItem": "{change.id}"`` in order to bind the uploaded document to the `change`:

.. http:example:: http/set-document-of-change.http
   :code:

Updating contract properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you can update contract properties which belong to the change.

You can update value `amount` and `amountNet` following next rules:

+-------------------------+------------------------------------------------------------------------+
| `valueAddedTaxIncluded` |                              `Validation`                              |
+-------------------------+------------------------------------------------------------------------+
|          true           | Amount should be greater than amountNet and differ by no more than 20% |
+-------------------------+------------------------------------------------------------------------+
|          false          |                  Amount and amountNet should be equal                  |
+-------------------------+------------------------------------------------------------------------+


.. http:example:: http/contracts-patch.http
   :code:

We see the added properties have merged with existing contract data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Fields that can be modified: `title`, `description`, `status`, `value.amount`, `value.amountNet`, `period`, `items`, `amountPaid.amount`, `amountPaid.amountNet`, `terminationDetails`.

See examples of `items` customization below. You can:

* update item:

.. http:example:: http/update-contract-item.http
   :code:

Applying the change
~~~~~~~~~~~~~~~~~~~

`Change` can be applied by switching to the ``active`` status.

In order to apply ``active`` status `dateSigned` field must be set.

After this `change` can't be modified anymore.

.. http:example:: http/apply-contract-change.http
   :code:

`dateSigned` field validation:

* for the first contract `change` date should be after `contract.dateSigned`;

* for all next `change` objects date should be after the previous `change.dateSigned`.

You can view all changes:

.. http:example:: http/view-all-contract-changes.http
   :code:

All changes are also listed on the contract view.

.. http:example:: http/view-contract.http
   :code:


Uploading documentation
-----------------------

Procuring entity can upload PDF files into the created contract. Uploading should
follow the :ref:`upload` rules.

.. http:example:: http/upload-contract-document.http
   :code:

`201 Created` response code and `Location` header confirm document creation.
We can additionally query the `documents` collection API endpoint to confirm the
action:

.. http:example:: http/contract-documents.http
   :code:

And again we can confirm that there are two documents uploaded.

.. http:example:: http/upload-contract-document-2.http
   :code:

In case we made an error, we can reupload the document over the older version:

.. http:example:: http/upload-contract-document-3.http
   :code:

And we can see that it is overriding the original version:

.. http:example:: http/get-contract-document-3.http
   :code:


.. index:: Enquiries, Question, Answer



Completing contract
-------------------

Before contract can be completed ``amountPaid`` field value should be set (regardless whether the contract was successful or unsuccessful).
Contract can be completed by switching to ``terminated`` status.
Let's perform these actions in single request:

.. http:example:: http/contract-termination.http
   :code:

Note that you can set/change ``amountPaid.amount``, ``amountPaid.amountNet``, ``amountPaid.valueAddedTaxIncluded`` values. ``amountPaid.currency`` field value is generated from ``Contract.value`` field.

If contract is unsuccessful reasons for termination ``terminationDetails`` should be specified.

Any future modification to the contract are not allowed.
