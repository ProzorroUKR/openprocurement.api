.. _has_awarding_order:

hasAwardingOrder
=================

Field `hasAwardingOrder` is a boolean field that indicates whether the award sorting will be applied due to awardCriteria
and awards will be created one by one or all awards will be created at once.

Possible values for `hasAwardingOrder` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/has-awarding-order-values.csv
   :header-rows: 1

hasAwardingOrder is `true`
--------------------------

Let's create a tender with `hasAwardingOrder` set to `true`:

.. http:example:: http/has-awarding-order-true-tender-post.http
   :code:

You can specify any kind of awardCriteria during creation tender with `hasAwardingOrder` set to `true`:
    * lowestCost
    * lifeCycleCost
    * ratedCriteria

Let's add lot to tender:

.. http:example:: http/has-awarding-order-true-tender-add-lot.http
   :code:

Let's look at tender with auction results:

.. http:example:: http/has-awarding-order-true-auction-results.http
   :code:

There is classic flow with award creation one by one due to awardCriteria sorting. Second award (for tender/lot)
will be generated in case the customer cancel decision for the first generated award.

hasAwardingOrder is `false`
---------------------------

Now let's create a tender with `hasAwardingOrder` set to `false`:

.. http:example:: http/has-awarding-order-false-tender-post.http
   :code:

Let's add lot to tender:

.. http:example:: http/has-awarding-order-false-tender-add-lot.http
   :code:

Let's look at tender with auction results:

.. http:example:: http/has-awarding-order-false-auction-results.http
   :code:

All awards have been generated at once after auction ends. Then the customer can choose any award as a winner.

Difference
----------

Let's look at completed tenders diff:

.. literalinclude:: json/has-awarding-order-false-auction-results.json
   :diff: json/has-awarding-order-true-auction-results.json

Difference for tender with `hasAwardingOrder` set to `false` comparing to `true` is that in tender
with `hasAwardingOrder` set to `false` after auction ends all awards have been created at once in status `pending`.
Then the customer can check the received offers sequentially or in the order in which he considers it necessary.

Update awards statuses for hasAwardingOrder = false
---------------------------------------------------
Let's consider cases with updating award statuses.

As an example let's use tender with 3 bidders. There are 3 awards with status pending in auction results:

.. http:example:: http/has-awarding-order-false-auction-results-example-1.http
   :code:

1) The customer decides that the winner is award1

.. http:example:: http/has-awarding-order-false-auction-results-example-1-activate-first-award.http
   :code:

In that case award1 becomes `active`, award2 and award3 are `pending`

.. http:example:: http/has-awarding-order-false-auction-results-example-1-results.http
   :code:

2) The customer cancels decision due to award1

.. http:example:: http/has-awarding-order-false-auction-results-example-2-cancel-first-award.http
   :code:

In that case award1 becomes `cancelled`, award2 and award3 are `pending`,
and award4 is being generated in status `pending` due to cancellation of the award1

.. http:example:: http/has-awarding-order-false-auction-results-example-2-results.http
   :code:

3) The customer rejects award4 and recognizes as the winner award2

In that case award1 still `cancelled`, award2 becomes `active`, and award3 are `pending`, award4 is `unsuccessful`:

.. http:example:: http/has-awarding-order-false-auction-results-example-3-results.http
   :code:

4) The customer cancel unsuccessful award4

In that case award1 still `cancelled`, award2 - `active`, and award3 - `pending`, award4 - `cancelled`
and award5 is being generated in status `pending` due to cancellation of the award4:

.. http:example:: http/has-awarding-order-false-auction-results-example-4-results.http
   :code:
