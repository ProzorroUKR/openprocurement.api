.. _min_bids_number:

minBidsNumber
====================

Field `minBidsNumber` is a integer field that indicates required number of propositions for the success of procedure.

Possible values for `minBidsNumber` field depends on `procurementMethodType` field:

.. csv-table::
   :file: csv/min-bids-number-values.csv
   :header-rows: 1

Configuration peculiarities
----------------------------

* The field value must be in the range from 1 to 9

Let's create a tender `belowThreshold` with configuration `minBidsNumber=0` and we will see error:

.. http:example:: http/min-bids-number-invalid-value-1.http
   :code:

Let's create a tender `belowThreshold` with configuration `minBidsNumber=10` and we will see error:

.. http:example:: http/min-bids-number-invalid-value-2.http
   :code:

* The value is indicated at the tender level. If the procedure contains >1 lots, then this value is applied equally to each lot:

.. note::
    Specify `minBidsNumber` at tender level `minBidsNumber=2` then `lot1=2; lot2=2; lotX=2`

* If at the end of the bid acceptance period, fewer bids than specified in the `minBidsNumber` field are submitted, the procedure automatically switches to the status `unsuccessful`, and the purchase is displayed as `The auction did not take place` on the site and on the official portal.

Let's create a tender `belowThreshold` with configuration `minBidsNumber=2` and 1 bid:

.. http:example:: http/min-bids-number-tender-post-1.http
   :code:

Let's look at tender after `active.tendering` is finished:

.. http:example:: http/min-bids-number-tender-unsuccessful.http
   :code:

* If the value `hasAuction:true`, `minBidsNumber=1` is set and `bids=1` are submitted after the end of the bid acceptance period, the system automatically registers the participant as a potential winner, the purchase is transferred to the status `active.qualification`.

Let's create a tender `belowThreshold` with configuration `minBidsNumber=1` and 1 bid:

.. http:example:: http/min-bids-number-tender-post-2.http
   :code:

Let's look at tender after `active.tendering` is finished, `auction` will be skipped and `active.qualification` period is started:

.. http:example:: http/min-bids-number-tender-qualification-1.http
   :code:

* If the `hasAuction:true` value is set, >=2 bids are submitted and the number of bids passes the minBidsNumber field check, the system activates the single `Auction` module.

Let's create a tender `belowThreshold` with configuration `minBidsNumber=2` and 2 bids:

.. http:example:: http/min-bids-number-tender-post-3.http
   :code:

Let's look at tender after `active.tendering` is finished, `auction` will be started:

.. http:example:: http/min-bids-number-tender-auction.http
   :code:

After `active.auction` is finished, the system should run `active.qualification`.
We look again at the `minBidsNumber:2` value and check for active bids. are there two of them? Yes, let's run `active.qualification`:

.. http:example:: http/min-bids-number-tender-qualification-2.http
   :code:
