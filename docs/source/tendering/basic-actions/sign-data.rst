
.. _sign-data:


Additional sign data
=====================

In the context of creating e-protocols, there was a need to impose a signature not only an object (an award or bid), but to have many general fields from the tender in the signature for the correct display of information.

For these purposes, it is agreed to proceed by adding boolean query parameter `opt_context` for endpoints for each necessary option (award, bid, cancellation, etc).

Parameter `opt_fields` can have such options:

* `true`, `1`, `True` - show additional context

* another values or missing parameter - don't show context

Award
------

Use `opt_context=true` as parameter for getting additional information for signing award:

.. http:example:: ./http/sign-data/sign-award-data.http
   :code:

As we can see there is additional field `context`, which has information from `tender` inside.


Bid
---

Use `opt_context=true` as parameter for getting additional information for signing bid:

.. http:example:: ./http/sign-data/sign-bid-data.http
   :code:

As we can see there is additional field `context`, which has information from `tender` inside.

If tender now in `active.tendering` status, only bidder can see this information.
If someone else wants to see sign data for bid, he will see an error:

.. http:example:: ./http/sign-data/sign-bid-data-forbidden.http
   :code:

Cancellation
------------

Use `opt_context=true` as parameter for getting additional information for signing cancellation:

.. http:example:: ./http/sign-data/sign-cancellation-data.http
   :code:

As we can see there is additional field `context`, which has information from `tender` inside.

