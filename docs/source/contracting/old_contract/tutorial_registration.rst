.. _old_contracting_tutorial_registration:

Tutorial (registration)
=======================

This tutorial describes how to work with regular contracting in tender system.

Contract will be created in the tender system after award activation.

Setting contract value
----------------------

Let's see the created contract with next request:

.. http:example:: http/tender-contract-get-contract-value.http
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

.. http:example:: http/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. http:example:: http/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. http:example:: http/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

You can upload contract documents. Let's upload contract document:

.. http:example:: http/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm document was added.

Let's see the list of contract documents:

.. http:example:: http/tender-contract-get-documents.http
   :code:

We can add another contract document:

.. http:example:: http/tender-contract-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm second document was uploaded.

Let's see the list of all added contract documents:

.. http:example:: http/tender-contract-get-documents-again.http
   :code:

Set contract signature date
---------------------------

There is a possibility to set custom contract signature date.
If the date is not set it will be generated on contract registration.

.. http:example:: http/tender-contract-sign-date.http
   :code:

Contract registration
---------------------

.. http:example:: http/tender-contract-sign.http
   :code:

Completing contract
-------------------

When the tender is completed, contract (that has been created in the tender system) is transferred to the contract system **automatically**.

Read more about working with regular contracting in contracting system in :ref:`old_contracting_tutorial` section.
