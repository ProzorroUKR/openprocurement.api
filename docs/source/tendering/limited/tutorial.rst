.. _limited_tutorial:

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

.. http:example:: http/tutorial/create-tender-procuringEntity.http
   :code:

We have `201 Created` response code, `Location` header and body with extra `id`, `tenderID`, and `dateModified` properties.

Let's check what tender registry contains:

.. http:example:: http/tutorial/tender-listing-after-procuringEntity.http
   :code:

We don't see internal `id` of tender, because tender appears in the listing from `active` status.


Creating tender for negotiation procedure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create tender for **negotiation** procedure you should set ``negotiation`` value for ``procurementMethodType``.

.. http:example:: http/tutorial/create-tender-negotiation-procuringEntity.http
   :code:


Creating tender for negotiation.quick procedure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create tender for **negotiation.quick** procedure you should set ``negotiation.quick`` value for ``procurementMethodType``.

.. http:example:: http/tutorial/create-tender-negotiation-quick-procuringEntity.http
   :code:


Tender activating
~~~~~~~~~~~~~~~~~

For activating **reporting**, **negotiation**, **negotiation.quick** procedures you should update status to ``active``:

.. http:example:: http/tutorial/tender-activating.http
   :code:

Let's see what listing of tenders reveals us:

.. http:example:: http/tutorial/active-tender-listing-after-procuringEntity.http
   :code:

We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp.


Modifying tender
~~~~~~~~~~~~~~~~

Let's update tender by supplementing it with all other essential properties:

.. http:example:: http/tutorial/patch-items-value-periods.http
   :code:

.. XXX body is empty for some reason (printf fails)

We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: http/tutorial/tender-listing-after-patch.http
   :code:


.. index:: Document

Uploading documentation
-----------------------

Procuring entity can upload documents and files into the created tender. Uploading should
follow the :ref:`upload` rules.

.. http:example:: http/tutorial/upload-tender-notice.http
   :code:

`201 Created` response code and `Location` header confirm document creation. 

In case we made an error, we can reupload the document over the older version:

.. http:example:: http/tutorial/update-tender-notice.http
   :code:

Awarding
--------

Adding supplier information
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Addition of supplier information is the same for all procedures.

Procuring entity registers supplier information for **reporting** procedure:

.. http:example:: http/tutorial/tender-award.http
   :code:

Procuring entity registers supplier information for **negotiation** procedure:

.. http:example:: http/tutorial/tender-negotiation-award.http
   :code:

You can notice that there is ``complaintPeriod`` record with ``startDate`` value generated.

Procuring entity registers supplier information for **negotiation.quick** procedure:

.. http:example:: http/tutorial/tender-negotiation-quick-award.http
   :code:

Award for **negotiation.quick** procedure also has ``complaintPeriod`` record with ``startDate`` value.


Uploading award documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can upload award documents only before awarding decision is confirmed. Let's add award document:

.. http:example:: http/tutorial/tender-award-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that document has been added.

Let's see the list of award documents:

.. http:example:: http/tutorial/tender-award-get-documents.http
   :code:

We can add another award document:

.. http:example:: http/tutorial/tender-award-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm second document has been added.

Let's see the list of all uploaded award documents:

.. http:example:: http/tutorial/tender-award-get-documents-again.http
   :code:


Award confirmation
~~~~~~~~~~~~~~~~~~

Procuring entity can confirm awarding decision:

.. http:example:: http/tutorial/tender-award-approve.http
   :code:

Award confirmation for **negotiation** procedure:

.. http:example:: http/tutorial/tender-negotiation-award-approve.http
   :code:

The difference between ``startDate`` and ``endDate`` in ``complaintPeriod`` record for **negotiation** is 10 days.

Award confirmation for **negotiation.quick** procedure:

.. http:example:: http/tutorial/tender-negotiation-quick-award-approve.http
   :code:

The difference between ``startDate`` and ``endDate`` in ``complaintPeriod`` record for **negotiation.quick** is 5 days.

Setting  contract value
-----------------------

By default contract value is set based on the award, but there is a possibility to set custom contract value. 

If you want to **lower contract value**, you can insert new one into the `amount` field.

.. http:example:: http/tutorial/tender-contract-set-contract-value.http
   :code:

`200 OK` response was returned. The value was modified successfully.

Setting value per item's unit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: http/tutorial/tender-contract-set-contract_items_unit-value.http
   :code:

`200 OK` response was returned with successfully set item.unit.value structure.

Item.unit.value.currency and Item.unit.value.valueAddedTaxIncluded are created using
contract.value(if exists), otherwise using tender.value data


Setting a single item unit value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: http/tutorial/tender-contract_items_unit_value.http
   :code:

`200 OK` response was returned with successfully set item.unit.value structure.

Item.unit.value.currency and Item.unit.value.valueAddedTaxIncluded are created using
contract.value(if exists), otherwise using tender.value data


Setting contract signature date
-------------------------------

There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field.

If this date is not set, it will be auto-generated on the date of contract registration.

.. http:example:: http/tutorial/tender-contract-sign-date.http
   :code:

Setting contract validity period
--------------------------------

Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`.

.. http:example:: http/tutorial/tender-contract-period.http
   :code:

Uploading contract documentation
--------------------------------

Contract documents can be uploaded only up until conclusion of the agreement. Let's add contract document:

.. http:example:: http/tutorial/tender-contract-upload-document.http
   :code:

`201 Created` response code and `Location` header confirm that document has been added.

Let's see the list of contract documents:

.. http:example:: http/tutorial/tender-contract-get-documents.http
   :code:

We can add another contract document:

.. http:example:: http/tutorial/tender-contract-upload-second-document.http
   :code:

`201 Created` response code and `Location` header confirm second document has been added.

Let's see the list of all uploaded contract documents:

.. http:example:: http/tutorial/tender-contract-get-documents-again.http
   :code:

Contract registration
---------------------

**Reporting** tender contract can be registered immediately after award confirmation:

.. http:example:: http/tutorial/tender-contract-sign.http
   :code:

**Negotiation** tender contract can be registered only after the stand-still (10 day period after the award confirmation):

.. http:example:: http/tutorial/tender-negotiation-contract-sign.http
   :code:

**Negotiation.quick** tender contract can be registered after the stand-still (5 day period after the award confirmation):

.. http:example:: http/tutorial/tender-negotiation-quick-contract-sign.http
   :code:

Cancelling tender
-----------------

Tender creator can cancel tender anytime (except when tender in status `active.auction` or in terminal status e.g. `unsuccessful`, `canceled`, `complete`).

The following steps should be applied:

1. Prepare cancellation request
2. Fill it with the protocol describing the cancellation reasons
3. 3. Passing complaint period(10 days),only for `negotiation` and `negotiation.quick`
4. Cancel the tender with the reasons prepared.

Only the request that has been activated (4th step above) has power to
cancel tender. I.e. you have to not only prepare cancellation request but
to activate it as well.

For cancelled cancellation you need to update cancellation status to `unsuccessful`
from `draft` or `pending`.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request for `reporting` procedure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should pass `reason` and `reasonType`, `status` defaults to `draft`.

There are four possible types of cancellation reason - tender was `noDemand`, `unFixable`, `forceMajeure` and `expensesCut`.

`id` is autogenerated and passed in the `Location` header of response.

.. http:example:: http/tutorial/prepare-cancellation.http
   :code:

You can change ``reasonType`` value to any of the above.

.. http:example:: http/tutorial/update-cancellation-reasonType.http
   :code:

Preparing the cancellation request for `negotiation` and `negotiation.quick` procedures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are five possible types of cancellation reason - tender was `noObjectiveness`,  `unFixable`, `noDemand`, `expensesCut`, `dateViolation`.

.. http:example:: http/tutorial/negotiation-prepare-cancellation.http
   :code:

You can change ``reasonType`` value to any of the above.

.. http:example:: http/tutorial/negotiation-update-cancellation-reasonType.http
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

Passing Complaint Period(only for `negotiation` and `negotiation.quick`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For activate complaint period, you need to update cancellation from `draft` to `pending`.

.. http:example:: http/tutorial/pending-cancellation.http
   :code:

When cancellation in `pending` status the tender owner is prohibited from all actions on the tender.

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if the complaint period(duration 10 days) is over and there were no complaints or
all complaints are canceled, then cancellation will automatically update status to `active`.