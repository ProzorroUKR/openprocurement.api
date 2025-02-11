.. _bid_items:


Bid Items
=========

Items in bid are available in all types of procedures


Creating bid with items
-----------------------

To create a bid with a procurement item, you need to pass the `items` field with a value containing a list of :ref:`BidItem` .

If you try to pass an item with an id that does not exist in tender.items, you will get an error:

.. http:example:: http/bid-items-localization/unsuccessful-create-bid-with-items.http
   :code:

VAT in `items.unit.value` can be only `False`. If you try to pass `True` you will see an error:

.. http:example:: http/bid-items-localization/unsuccessful-create-bid-with-items-VAT.http
   :code:

Let's send correct data:

.. http:example:: http/bid-items-localization/successfuly-create-bid-with-items.http
   :code:


Update bid items
----------------

You can update `quantity` and `unit` in bid items.

To update the data in items, you need to pass all elements from the list along with all data; otherwise, the data that is not passed will be lost:

.. http:example:: http/bid-items-localization/update-bid-items.http
   :code:


.. _bid_product_items:


Product in bid items
=====================

Instead of using eligibleEvidence in criteria and evidence in requirementResponses, now you can use product in bid.items.

Procedures with product in bid items
------------------------------------

Product in bid items is available in these procedures:
 - aboveThresholdUA
 - aboveThresholdEU
 - belowThreshold
 - competitiveDialogueUA
 - competitiveDialogueEU
 - competitiveDialogueUA.stage2
 - competitiveDialogueEU.stage2
 - competitiveOrdering
 - closeFrameworkAgreementUA
 - esco
 - priceQuotation


Create bid with product in items
--------------------------------

All of you need it's pass product identificator of active product from market to field `product` in bid.items.


If you pass a non-existent identifier, you will get an error:

.. http:example:: http/bid-items-localization/item-product-not-found.http
   :code:


if you try to pass identifier of product with `hidden` status, you'll also get error:

.. http:example:: http/bid-items-localization/item-product-not-active.http
   :code:


So if all rules are met, you can create bid with product in items:

.. http:example:: http/bid-items-localization/bid-with-item-product-created.http
   :code:


Update product in bid items
----------------------------

You can change product identifier using `PATCH` method on bid(All validations on creation also work on update):

.. http:example:: http/bid-items-localization/update_bid-with-item-product.http
   :code: