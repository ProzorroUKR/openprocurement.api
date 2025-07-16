.. _has_auction:

hasAuction
==========

Field `hasAuction` is a boolean field that indicates whether the tender has an auction or not.
Tender will never switch to `active.auction` status if `hasAuction` is `false`.

Possible values for `hasAuction` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/has-auction-values.csv
   :header-rows: 1

hasAuction is `true`
--------------------

Let's create a tender with `hasAuction` set to `true`:

.. http:example:: http/has-auction-true-tender-post.http
   :code:

And add lot to it:

.. http:example:: http/has-auction-true-tender-add-lot.http
   :code:

Field `minimalStep` is required for tenders with auction.

* If it is non-lots tender then this fields is required during activation in tender.

* It it is lots tender - then this field is required in lots but in tender this field is rogue and it doesn't set as minimal value of all `minimalStep` in lots.

If during activation tender has lots and own `minimalStep`, then we will see an error that `minimalStep` is rogue field for tender:

.. http:example:: http/has-auction-true-tender-with-lots-minimal-step-rogue.http
   :code:

Let's look at completed tender:

.. http:example:: http/has-auction-false-tender-complete.http
   :code:

hasAuction is `false`
---------------------

Now let's create a tender with `hasAuction` set to `false`:

.. http:example:: http/has-auction-false-tender-post.http
   :code:

You can see that there is no `minimalStep` field in the request body, because tender with no auction doesn't have `minimalStep` field.

And add lot to it:

.. http:example:: http/has-auction-false-tender-add-lot.http
   :code:

There is also no `minimalStep` field in the request body.

Let's look at completed tender:

.. http:example:: http/has-auction-false-tender-complete.http
   :code:

Difference
----------

Let's look at completed tenders diff:

.. literalinclude:: json/has-auction-false-tender-complete.json
   :diff: json/has-auction-true-tender-complete.json

Differences for tender with `hasAuction` set to `false` comparing to `true` are:

* has no `submissionMethod` field

* has no `minimalStep` field

* has no `auctionPeriod` field

* has no `auctionUrl` field

* has no `participationUrl` field
