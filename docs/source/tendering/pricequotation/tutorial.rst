.. _pricequotation_tutorial:

Tutorial
========

.. index:: Tender

Configuration
-------------

The set of possible configuration values:

.. csv-table::
   :file: csv/config.csv
   :header-rows: 1

You can look for more details in :ref:`config` section.

Creating tender
---------------

Let's provide the data attribute in the submitted body :

.. http:example:: http/tender-post-attempt-json-data.http
   :code:

Success! Now we can see that new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created tender: its internal
`id` (that matches the `Location` segment), its official `tenderID` and
`dateModified` datestamp stating the moment in time when tender was last
modified.  Note that tender is created with `draft` status.

.. note::

    User receives `access`: `token` with which operations as a `Procuring Entity` role are accessible.

Price Quotation procedure has ``procurementMethodType``: ``priceQuotation`` and ``procurementMethod``: ``selective``.

Let's access the URL of the created object (the `Location` header of the response):

.. http:example:: http/blank-tender-view.http
   :code:

We can see the same response we got after creating tender.

Modifying tender
----------------

Procuring Entity can modify tender before publishing. 
Let's update tender by supplementing it with all other essential properties:

.. http:example:: http/patch-tender-data.http
   :code:

We see the added properties have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp.

Checking the listing again reflects the new modification date:

.. http:example:: http/tender-listing-after-patch.http
   :code:

Publishing tender (deprecated)
------------------------------
   
After creation Procuring Entity publishes procedure by changing status to `draft.publishing` where **priceQuotationBot** robot runs validation of the procedure and supplement procedure with additional data taken from ProZorro e-Catalogues database including `shortListedFirms`.

.. http:example:: http/publish-tender.http
   :code:


After successful validation priceQuotationBot transmit procedure to status: `active.tendering` 

.. http:example:: http/tender-after-bot-active.http
   :code:

In case if procedure do not pass validation due to invalid options, it will be switched to status: `draft.unsuccessful` by the **priceQuotationBot**.

.. http:example:: http/tender-after-bot-unsuccessful.http
   :code:

.. index:: Document

Activating tender
-----------------

After creation Procuring Entity can activate tender by changing status to `active.tendering`.

During activation CBD runs some validations:

* Existence of item profile in catalogue

* Profile should be active or general

* Existence of related agreement

* Equality of profile agreement and related agreement in tender

* Agreement should not be in terminated status


If Procuring Entity will try to activate PQ procedure with non-existed profile in catalogue, we will see error:

.. http:example:: http/tender-with-non-existed-profile.http
   :code:

If profile isn't in active status, we will see error:

.. http:example:: http/tender-with-non-active-profile.http
   :code:

In case profile agreement and related agreement in tender aren't equal, the next error will be generated:

.. http:example:: http/tender-agreement-mismatch-in-profile.http
   :code:

If agreement is in terminated status:

.. http:example:: http/tender-agreement-terminated.http
   :code:

If PQ procedure matches all requirements, it will be switched to `active.tendering`:

.. http:example:: http/tender-active.http
   :code:


Bid submission
--------------

Registering bid
~~~~~~~~~~~~~~~
Tender status ``active.tendering`` allows registration of bids.

If bid `tenderer` is not a member of agreement, than we will see an error during registration of bid:

.. http:example:: http/register-bidder-not-member.http
   :code:

Bidder can register a bid with ``draft`` status:

.. http:example:: http/register-bidder.http
   :code:

.. note::

    User receives `access`: `token` with which operations as a `Supplier` role are accessible.


and approve to pending status:

.. http:example:: http/activate-bidder.http
   :code:

Modifying bid
~~~~~~~~~~~~~~~
   
Bid can be updated until the end of tender period. 

.. http:example:: http/patch-bidder.http
   :code:
   
Proposal Uploading
~~~~~~~~~~~~~~~~~~

Then bidder should upload proposal document(s):

.. http:example:: http/upload-bid-proposal.http
   :code:

It is possible to check the uploaded documents:

.. http:example:: http/bidder-documents.http
   :code:
   
.. index:: Awarding

Awarding process
----------------

After the tender period end date, system automatically creates `award` in `pending` status for the bid with the most economically advantageous price.

.. http:example:: http/awards-listing.http
   :code:

Procuring Entity can accept `award` by transferring it to status: `active`.

.. http:example:: http/award-active.http
   :code:

Let's check the listing of `awards`:

.. http:example:: http/awards-listing-after-activation.http
   :code:

Procuring Entity can cancel `award` after acceptance by changing `award` status to `cancelled`:

.. http:example:: http/award-cancelled.http
   :code:

After canceling `award` system creates `second` `award` for the same bid in status: `pending`:

.. http:example:: http/awards-listing-after-cancellation.http
   :code:

If the offer of the Participant with the lowest price meets the requirements, Procuring Entity uploads a document that recognizes the offer as the Winner `(awards:status:active)`.
If it does not meet the requirements, Procuring Entity downloads a protocol confirming its decision to reject the Participant and rejects such an offer `(awards:status:unsuccessful)`.
The system leads to the evaluation of the next one with most economically advantageous price `(awards:status:pending)`.

Let's decline `award` by transferring it to status: `unsuccessful`.

.. http:example:: http/award-unsuccesful.http
   :code:

In that case `Award` will be granted to the next bid with most economically advantageous price.

Let's check the listing of `awards`:

.. http:example:: http/awards-listing-after-unsuccesful.http
   :code:

Procuring Entity can accept second bidder `award` by transferring it to status: `active`.

.. http:example:: http/award-active-2.http
   :code:

Let's check the listing of `awards`:

.. http:example:: http/awards-listing-after-activation-2.http
   :code:

.. note::

    In the case of `award` being transferred to `unsuccessful` status for the last bid procedure will inherit termination status: **`unsuccessful`**.


.. index:: Setting Contract

Setting Contract
----------------

There are to modes of contracting depending on system configuration:

Regular contracting
~~~~~~~~~~~~~~~~~~~

In regular contacting the contract will be created in tender system first.

Read more about working with regular contracting in tendering system in :ref:`old_contracting_tutorial_registration` section.

When the tender is completed (after contracts activation), contract (that has been created in the tender system) is transferred to the contract system **automatically**.

Read more about working with regular contracting in contracting system in :ref:`old_contracting_tutorial` section.

EContracting
~~~~~~~~~~~~

In EContracting the contract is created directly in contracting system.

.. note::
    Some of data will be mirrored to tender until contract will be activated for backward compatibility.

Read more about working with EContracting in contracting system in :ref:`econtracting_tutorial` section.

   
Cancelling tender
-----------------

Tender creator can cancel tender anytime (except when tender in terminal status e.g. `draft.unsuccessful`, `unsuccessful`, `cancelled`, `complete`).

The following steps should be applied:

1. Prepare cancellation request.
2. Fill it with the protocol describing the cancellation reasons.
3. Cancel the tender with the prepared reasons.

Only the request that has been activated (3rd step above) has power to
cancel tender.  I.e.  you have to not only prepare cancellation request but
to activate it as well.

For cancelled cancellation you need to update cancellation status to `unsuccessful`
from `draft` or `pending`.

See :ref:`cancellation` data structure for details.

Preparing the cancellation request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should pass `reason` and `reasonType`, `status` defaults to `draft`.

There are four possible types of cancellation reason - tender was `noDemand`, `unFixable`, `forceMajeure` and `expensesCut`.

`id` is autogenerated and passed in the `Location` header of response.

.. http:example:: http/prepare-cancellation.http
   :code:

You can change ``reasonType`` value to any of the above.

.. http:example:: http/update-cancellation-reasonType.http
     :code:

Filling cancellation with protocol and supplementary documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is required. Without documents you can't update tender status.

Upload the file contents

.. http:example:: http/upload-cancellation-doc.http
   :code:

Change the document description and other properties


.. http:example:: http/patch-cancellation.http
   :code:

Upload new version of the document


.. http:example:: http/update-cancellation-doc.http
   :code:

Activating the request and cancelling tender
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:example:: http/active-cancellation.http
   :code:
