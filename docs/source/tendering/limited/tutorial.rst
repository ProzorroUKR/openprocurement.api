.. _limited_tutorial:

Tutorial
========

Configuration
-------------

The set of possible configuration values for `reporting`:

.. csv-table::
   :file: csv/config-reporting.csv
   :header-rows: 1

The set of possible configuration values for `negotiation`:

.. csv-table::
   :file: csv/config-negotiation.csv
   :header-rows: 1

The set of possible configuration values for `negotiation.quick`:

.. csv-table::
   :file: csv/config-negotiation-quick.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

Tender creation
---------------

You can create three procedures: 
 * ``reporting`` - reporting with no stand-still period 
 * ``negotiation`` - negotiation procedure with 10 day stand-still before contract registration
 * ``negotiation.quick`` - quick negotiation procedure with 5 day stand-still before contract registration


Creating tender for reporting procedure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create tender for **reporting** procedure you should set ``reporting`` value for ``procurementMethodType``.

For **reporting** procedure there is required field `cause`. It is required if field `procurementMethodRationale` is empty, `procuringEntity.kind` is not other and tender value amount is bigger than:

    * 100 000 for goods,
    * 200 000 for services,
    * 1 500 000 for works.

Let's try to create tender with value amount bigger than threshold and without `procurementMethodRationale`:

.. http:example:: http/tutorial/create-tender-reporting-invalid.http
   :code:

Let's add `cause` and `causeDescription` and then create a tender:

.. http:example:: http/tutorial/create-tender-reporting-procuringEntity.http
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

.. index:: Setting Contract

Setting Contract
----------------

All operations with contract moved to :ref:`econtracting`


Contract registration
~~~~~~~~~~~~~~~~~~~~~~

**Reporting** tender contract can be registered immediately after award confirmation:

.. http:example:: http/tutorial/tender-contract-sign.http
   :code:

**Negotiation** tender contract can be registered only after the stand-still (10 day period after the award confirmation):

.. http:example:: http/tutorial/tender-negotiation-contract-sign.http
   :code:

**Negotiation.quick** tender contract can be registered after the stand-still (5 day period after the award confirmation):

.. http:example:: http/tutorial/tender-negotiation-quick-contract-sign.http
   :code:

Confidential documents for contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a tender, the customer selects one of the items (`cause`) from the drop-down list of reasons for applying the purchase contract report.
If one of the particular reasons is used, the files (documents) that the customer uploads to the contract and changes to the contract (`"documentOf": "contract"` and `"documentOf": "change"`) must be hidden in such reporting procedure.

Documents should be confidential if reporting has one ot the causes:

    * criticalInfrastructure
    * civilProtection
    * RNBO
    * lastHope
    * UZ
    * defencePurchase

and has one of document types:

    * contractSigned - Signed contract
    * contractAnnexe - Annexes to the contract

Confidentiality should be applied for documents, in case of application of the above causes. It is required to add `confidentialityRationale` with `confidentiality: buyerOnly`.

Let's add documents to contract and set `confidentiality` as public, we will see an error:

.. http:example:: http/tutorial/tender-reporting-contract-conf-docs-as-public.http
   :code:

Change `confidentiality` as `buyerOnly` and look what we've got:

.. http:example:: http/tutorial/tender-reporting-contract-conf-docs-wo-rationale.http
   :code:

Let's add `confidentialityRationale`:

.. http:example:: http/tutorial/tender-reporting-contract-conf-docs.http
   :code:

The customer see these kind of documents and can download:

.. http:example:: http/tutorial/get-tender-reporting-contract-conf-docs-by-owner.http
   :code:

All others can't read the document:

.. http:example:: http/tutorial/get-tender-reporting-contract-conf-docs-by-public.http
   :code:

Nobody but the owner can download the confidential document:

.. http:example:: http/tutorial/upload-tender-reporting-contract-conf-doc-by-public.http
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