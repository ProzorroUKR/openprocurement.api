.. _multicurrency:

Multi currency
==============

The requestForProposal procedure can be multi currency for donors.
To create such type of procedure it is required to set config `valueCurrencyEquality:false` and add `funders` field.

In this way, it will be possible to add a price list of items to the procedure in different currency. The price list will help to visually show which parts make up the total price of the participant for each item separately.

Let's create tender with configuration `valueCurrencyEquality:false` and `funders` field, add lots for it and activate it:

.. http:example:: http/multi-currency/tender.http
   :code:

Now the participant can register bid.

It is required to add `items` for tender with field `funders`. If there are no `items` in bid, we will see an error:

.. http:example:: http/multi-currency/post-bid-without-items.http
   :code:

Also it is required to add `value` in `items.unit` for tender with field `funders`. If there are no `value` in `bid.items.unit`, we will see an error:

.. http:example:: http/multi-currency/post-bid-without-values-in-unit-items.http
   :code:

Quantity of items in bid should be equal to quantity of tender items related to lot set in `lotValues`:

.. http:example:: http/multi-currency/post-bid-with-items-less-than-in-tender.http
   :code:

Items ids in bid should correspond to items ids in tender and belong to the same `relatedLot` as set in bid:

.. http:example:: http/multi-currency/post-bid-with-items-related-to-another-lot.http
   :code:

For each nomenclature (items), the participant indicates the price per unit. He can specify different currencies:

.. http:example:: http/multi-currency/post-add-valid-bid.http
   :code:

The requirements for bid registration:

* The `currency` value for each unit price: may be different, the value may NOT match the Currency value for the overall quote and may NOT be the same at the lot level; the value may NOT correspond to the value of the Currency specified by the customer in the tender in the expected purchase price

* The total cost of Lot-level Unit Prices may NOT equal the total bid price

* The value of VAT must correspond to the value specified by the customer in the tender

* If the participant plans to give the customer a so-called discount, he can specify the value 0 for certain items in the Price per unit value

Let's try to change VAT value in `bid.items.unit` to different than False and we will see the error:

.. http:example:: http/multi-currency/patch-invalid-bid-unit.http
   :code:

An auction is not provided for such purchases.

Let's choose the winner and look at the contract. As we can see all unit prices are transferred to the contract:

.. http:example:: http/multi-currency/contract.http
   :code:

The total offer price and the price per unit are adjusted both upwards and downwards.

At the same time, the total cost of the price per unit can be not equal to the total price of the offer.

VAT can be changed at the contract level (must be changed in both contract.value and contract.items.unit.value at the same time).

Let's patch contract values:

.. http:example:: http/multi-currency/contract-patch.http
   :code:

Then let's activate contract to check whether it is possible to change general sum of unit values greater than we have in contract value:

.. http:example:: http/multi-currency/contract-activated.http
   :code:
