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

At first buyer and supplier should fill signer information and fill all required fields the same as in :ref:`contracting_tutorial`.

It is also required to add contract signature document type from each participant (supplier and buyer).
If you try activate contract without signatures you'll get error:

.. http:example:: http/contract-activating-wo-signature-error.http
   :code:

Before adding signature there will be validations that all required fields are set:

.. http:example:: http/contract-add-signature-in-not-ready-contract.http
   :code:

Supplier adds signature document using his token (`supplier_token`) which he got during access query:

.. http:example:: http/contract-supplier-add-signature-doc.http
   :code:

If there is at least one signature in contract, it is forbidden to patch contract:

.. http:example:: http/patch-contract-forbidden.http
   :code:

Buyer adds signature document using his token (`buyer_token`) which he got during access query:

.. http:example:: http/contract-buyer-add-signature-doc.http
   :code:

If all required signatures are completed, the contract will automatically transition to the `active` status:

.. http:example:: http/get-active-contract.http
   :code:
