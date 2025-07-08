.. _econtracting_tutorial:

Tutorial
========

Creating contract
-----------------

Let's say that we have conducted tender with award. When the award is activated, a contract is **automatically** created in the tender with a limited set of fields(`id`, `awardID`, `status`, `date`, `value`) and in the contracting module with a full set of fields(:ref:`Econtract`) in ``pending`` status.

*Brokers (eMalls) can't create contracts in the contract system.*

A contract is created with additional fields:

* `contractTemplateName` - copied from tender if exists (more about it in :ref:`contract-template-name`)

A PQ contract is created with additional fields:

* `attributes` - formed from requirements and responses in tender


Getting contract
----------------

Contract in the tender system

.. http:example:: http/example-contract.http
   :code:

*Contract id is the same in both tender and contract system.*

Let's access the URL of the created object:

.. http:example:: http/contract-view.http
   :code:

Getting access
---------------

Read more :ref:`authorization-from-different-platforms-new`

For getting access for buyer or supplier endpoint `contracts/{contract_id}/access` is used after contract was created.

Algorith of getting access:

* POST `/access` with identifier of client - returns token for client

Main action is POST `/access` - a query with a client identifier determines whether it is a buyer or supplier.
If the identifier does not match any of the entities, an error is issued:

.. http:example:: http/contract-access-invalid.http
   :code:

If identifier is found, then we validate whether authenticated user is an owner for this role:

.. http:example:: http/contract-access-owner-invalid.http
   :code:

If identifier is found and owner matches, then the token is set according to the entity for supplier or buyer:

.. http:example:: http/contract-access-by-buyer.http
   :code:

If buyer get access, we will see in response new `transfer` token too.

After token generation, it is allowed to regenerate token, make new POST request with this identifier:

.. http:example:: http/contract-access-by-buyer-2.http
   :code:

**NOTE:**
Then user can modify contract as buyer only using the last generated token.

After token was regenerated, previous token can not be used for updating contract:

.. http:example:: http/contract-patch-by-buyer-1-forbidden.http
   :code:

The same algorithm will be for supplier access.

Let's require access for supplier:

.. http:example:: http/contract-access-by-supplier.http
   :code:

**WARNING:**
It is allowed to get access only during contract is `pending`.

Activating contract
-------------------

If contract was created using new flow with set `contract_owner` in tender for `suppliers` and `buyers` than for activating electronic contract, signer information and all participants signature are required.

To activate contract it is required to add contract signature document type from each participant (supplier and buyer).

If both sides signed the current version of contract, than contract becomes `active`.

Supplier adds signature document using his token (`supplier_token`) which he got during access query:

.. http:example:: http/contract-supplier-add-signature-doc.http
   :code:

Buyer adds signature document using his token (`buyer_token`) which he got during access query:

.. http:example:: http/contract-buyer-add-signature-doc.http
   :code:

If all required signatures are completed, the contract will automatically transition to the `active` status:

.. http:example:: http/get-active-contract.http
   :code:

New versions of contract
=========================

If one of sides doesn't agree to sign current version of contract, there is an opportunity to create a new version of contract.

Flow:

* create a cancellation of current version of contract

* POST new version o contract with updates

* sign new version and wait till another side agrees to sign (or create new version by his side)

Cancellations
--------------

It is allowed to cancel current version of contract and create new one only before signature and during contract is `pending`.

For example, if buyer already sign the contract, it is forbidden for him cancel this version:

.. http:example:: http/contract-buyer-cancel-contract-forbidden.http
   :code:

To cancel current version of contract, participant of contract should create a cancellation with reason:

.. http:example:: http/contract-supplier-cancels-contract.http
   :code:

Let's look at contract:

.. http:example:: http/cancellation-of-contract.http
   :code:

It is forbidden to add more than one cancellation:

.. http:example:: http/cancellation-of-contract-duplicated.http
   :code:

After cancellation created, there is forbidden to sign contract:

.. http:example:: http/contract-supplier-add-signature-forbidden.http
   :code:

Create new contract version
---------------------------

Then the same participant should create a new version of contract.

If buyer tries to create a new version, he will see an error, as supplier cancelled previous contract:

.. http:example:: http/contract-buyer-post-contract-forbidden.http
   :code:

Allowed fields for updating:

* period
* contractNumber
* items.unit
* items.quantity
* value
* title
* title_en
* description
* description_en
* dateSigned
* signerInfo (for supplier or buyer depends on who cancelled contract)

If participant tried to update another field, he will see an error:

.. http:example:: http/contract-supplier-post-contract-invalid.http
   :code:

Let's update fields `period`, `contractNumber` and `signerInfo.name` using token for supplier:

.. http:example:: http/contract-supplier-post-contract-version.http
   :code:

Success! Let's look at previous version of contract, it became `cancelled` and cancellation now is `active`:

.. http:example:: http/get-previous-contract-version.http
   :code:

Let's look at all contracts in tender:

.. http:example:: http/get-tender-contracts.http
   :code:

After that new round of signatures begins.

Supplier and buyer can sign this new version of contract if they agreed with changes or create new version if disagreed.