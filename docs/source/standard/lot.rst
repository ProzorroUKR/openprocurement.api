.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Lot

.. _Lot:

Lot
===

Schema
------

:id:
    string, auto-generated

:title:
   string, multilingual

   The name of the tender lot.

:description:
   string, multilingual

   Detailed description of tender lot.

:value:
   :ref:`value`, required

   Total available tender lot budget. Bids greater then ``value`` will be rejected.

:guarantee:
    :ref:`Guarantee`

    Bid guarantee

:minimalStep:
   :ref:`value`, required

   The minimal step of auction (reduction). Validation rules:

   * `amount` should be less then `Lot.value.amount`
   * `currency` should either be absent or match `Lot.value.currency`
   * `valueAddedTaxIncluded` should either be absent or match `Lot.value.valueAddedTaxIncluded`

:auctionPeriod:
   :ref:`period`, read-only

   Period when Auction is conducted.

:auctionUrl:
    url

    A web address for view auction.

:status:
   string

   :`active`:
       Active tender lot
   :`unsuccessful`:
       Unsuccessful tender lot
   :`complete`:
       Completed tender lot
   :`cancelled`:
       Cancelled tender lot

   Status of the Lot.

Workflow
--------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="complete"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
         A -> B;
         A -> C;
         A -> D;
    }

\* marks initial state
