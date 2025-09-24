.. _contract-owner:


Providing contract owner
=========================

For further contracting using new flow (:ref:`econtracting_tutorial`) it is possible provide contract owner (SEDO).

For buyer it should be set in one of fields along with `signerInfo`:

* `procuringEntity`
*  `buyers`

For supplier it should be set in `bid.tenderers` along with `signerInfo`.

Field `contract_owner` can be set along with `contractTemplateName` in tender and `signerInfo` in object.

If there is no `signerInfo` in object or there is no `contractTemplateName` in tender, we will see an error:

.. http:example:: ./http/contract-owner/add-contract-owner-no-template.http
   :code:

In field `contract_owner` it is allowed to set one of the brokers which has the 6th level of accreditation.

In future contract they will have opportunity to generate token and deal with contract based on their role (`supplier` or `buyer`).

If broker which set as a `contract_owner` doesn't have the 6th level of accreditation, we will see an error:

.. http:example:: ./http/contract-owner/add-contract-owner-invalid-broker.http
   :code:

Successful adding `contract_owner` along with `contractTemplateName` in tender and `signerInfo` in `procuringEntity`:

.. http:example:: ./http/contract-owner/add-contract-owner-buyer.http
   :code:

Successful adding `contract_owner` along with `contractTemplateName` in tender and `signerInfo` in `bid.tenderers`:

.. http:example:: ./http/contract-owner/add-contract-owner-supplier.http
   :code:

When contract is created, these brokers can generate token to deal with contract.

Let's look at contract, after creation, we will see `contract_owner` in `buyer` and `suppliers` objects:

.. http:example:: ./http/contract-owner/get-contract-owners.http
   :code:
