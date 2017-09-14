.. _tutorial:

Tutorial
========

Tender creation
---------------

You can create three procedures: 
 * ``reporting`` - reporting with no stand-still period 
 * ``negotiation`` - negotiation procedure with 10 day stand-still before contract registration
 * ``negotiation.quick`` - quick negotiation procedure with 5 day stand-still before contract registration


Creating tender for reporting procedure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create tender for **reporting** procedure you should set ``reporting`` value for ``procurementMethodType``.

Let’s create a tender:

.. include:: tutorial/create-tender-procuringEntity.http
   :code:

We have `201 Created` response code, `Location` header and body with extra `id`, `tenderID`, and `dateModified` properties.

Let's check what tender registry contains:

.. include:: tutorial/tender-listing-after-procuringEntity.http
   :code:

We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.


Creating tender for negotiation procedure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create tender for **negotiation** procedure you should set ``negotiation`` value for ``procurementMethodType``.

.. include:: tutorial/create-tender-negotiation-procuringEntity.http
   :code:


Creating tender for negotiation.quick procedure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create tender for **negotiation.quick** procedure you should set ``negotiation.quick`` value for ``procurementMethodType``.

.. include:: tutorial/create-tender-negotiation-quick-procuringEntity.http
   :code:


Modifying tender
~~~~~~~~~~~~~~~~

Let's update tender by supplementing it with all other essential properties:

.. include:: tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. include:: tutorial/tender-listing-after-patch.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload documents and files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. include:: tutorial/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation. 

In case we made an error, we can reupload the document over the older version:

.. include:: tutorial/update-tender-notice.http
   :code:

Awarding
--------

Adding supplier information
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Addition of supplier information is the same for all procedures.

Procuring entity registers supplier information for **reporting** procedure:

.. include:: tutorial/tender-award.http
   :code:

Procuring entity registers supplier information for **negotiation** procedure:

.. include:: tutorial/tender-negotiation-award.http
   :code:

You can notice that there is ``complaintPeriod`` record with ``startDate`` value generated.

Procuring entity registers supplier information for **negotiation.quick** procedure:

.. include:: tutorial/tender-negotiation-quick-award.http
   :code:

Award for **negotiation.quick** procedure also has ``complaintPeriod`` record with ``startDate`` value.


Uploading award documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can upload award documents only before awarding decision is confirmed. Let's add award document:

.. include:: tutorial/tender-award-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that document has been added.

Let's see the list of award documents:

.. include:: tutorial/tender-award-get-documents.http
   :code:

We can add another award document:

.. include:: tutorial/tender-award-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm second document has been added.

Let's see the list of all uploaded award documents:

.. include:: tutorial/tender-award-get-documents-again.http
   :code:


Award confirmation
~~~~~~~~~~~~~~~~~~

Procuring entity can confirm awarding decision:

.. include:: tutorial/tender-award-approve.http
   :code:

Award confirmation for **negotiation** procedure:

.. include:: tutorial/tender-negotiation-award-approve.http
   :code:

The difference between ``startDate`` and ``endDate`` in ``complaintPeriod`` record for **negotiation** is 10 days.

Award confirmation for **negotiation.quick** procedure:

.. include:: tutorial/tender-negotiation-quick-award-approve.http
   :code:

The difference between ``startDate`` and ``endDate`` in ``complaintPeriod`` record for **negotiation.quick** is 5 days.

Setting  contract value
-----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value. 

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. include:: tutorial/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting value per item's unit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: tutorial/tender-contract-set-contract_items_unit-value.http
   :code:

`200 OK` response was returned with successfully set item.unit.value structure.


Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. include:: tutorial/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. include:: tutorial/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

Contract documents can be uploaded only up until conclusion of the agreement. Let's add contract document:

.. include:: tutorial/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that document has been added.

Let's see the list of contract documents:

.. include:: tutorial/tender-contract-get-documents.http
   :code:

We can add another contract document:

.. include:: tutorial/tender-contract-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm second document has been added.

Let's see the list of all uploaded contract documents:

.. include:: tutorial/tender-contract-get-documents-again.http
   :code:

Contract registration
---------------------

**Reporting** tender contract can be registered immediately after award confirmation:

.. include:: tutorial/tender-contract-sign.http
   :code:

**Negotiation** tender contract can be registered only after the stand-still (10 day period after the award confirmation):

.. include:: tutorial/tender-negotiation-contract-sign.http
   :code:

**Negotiation.quick** tender contract can be registered after the stand-still (5 day period after the award confirmation):

.. include:: tutorial/tender-negotiation-quick-contract-sign.http
   :code:

Cancelling tender
-----------------

Procuring entity can cancel tender anytime. The following steps should be applied:

1. Prepare cancellation request
2. Fill it with the protocol describing the cancellation reasons 
3. Cancel the tender with the reasons prepared.

Only the request that has been activated (3rd step above) has power to
cancel tender. I.e. you have to not only prepare cancellation request but
to activate it as well.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should pass `reason`, `status` defaults to `pending`.

`id` is autogenerated and passed in the `Location` header of response.

.. include::  tutorial/prepare-cancellation.http
   :code:

There are two possible types of cancellation reason - tender was `cancelled` or `unsuccessful`. By default 
``reasonType`` value is `cancelled`.

You can change ``reasonType`` value to `unsuccessful`.

.. include::  tutorial/update-cancellation-reasonType.http
   :code:


Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upload the file contents

.. include::  tutorial/upload-cancellation-doc.http
   :code:

Change the document description and other properties


.. include::  tutorial/patch-cancellation.http
   :code:

Upload new version of the document


.. include::  tutorial/update-cancellation-doc.http
   :code:

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include::  tutorial/active-cancellation.http
   :code:
