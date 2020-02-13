Tutorial
========

When customer needs to change current broker this customer should provide new preferred broker with ``transfer`` key for an object. Then new broker should create `Transfer` object and send request with `Transfer` ``id`` and ``transfer`` key (received from customer) in order to change object's owner.

.. toctree::
   :maxdepth: 4

   tenders
   contracts
   plans
   agreements
