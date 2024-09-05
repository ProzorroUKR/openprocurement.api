
.. _sign-data:


Additional sign data
=====================

In the context of creating e-protocols, there was a need to impose a signature not only an object (an award or bid), but to have many general fields from the tender in the signature for the correct display of information.

For these purposes, it is agreed to proceed by creating separate endpoints for each necessary option (award, bid, cancellation, etc).

Award
------

There is an endpoint for getting additional information for signing award:

.. http:example:: ./http/sign-data/sign-award-data.http
   :code:

As we can see there is additional field `context`, which has information from `tender` inside.


Bid
---

There is an endpoint for getting additional information for signing bid:

.. http:example:: ./http/sign-data/sign-bid-data.http
   :code:

As we can see there is additional field `context`, which has information from `tender` inside.

If tender now in `active.tendering` status, only bidder can see this information.
If someone else wants to see sign data for bid, he will see an error:

.. http:example:: ./http/sign-data/sign-bid-data-forbidden.http
   :code:
