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

   Absent in :ref:`esco`

:guarantee:
    :ref:`Guarantee`

    Bid guarantee

    Absent in :ref:`limited`
    
:date:
    string, :ref:`date`, auto-generated
    
:minimalStep:
   :ref:`value`, required

   The minimal step of auction (reduction). Validation rules:

   * `amount` should be less then `Lot.value.amount`
   * `currency` should either be absent or match `Lot.value.currency`
   * `valueAddedTaxIncluded` should either be absent or match `Lot.value.valueAddedTaxIncluded`

   Absent in :ref:`limited` and :ref:`esco`

:auctionPeriod:
   :ref:`period`, read-only

   Period when Auction is conducted.

   Absent in :ref:`limited`

:auctionUrl:
    url

    A web address for view auction.

    Absent in :ref:`limited`

:status:
   string

   :`active`:
       Active tender lot (active)
   :`unsuccessful`:
       Unsuccessful tender lot (unsuccessful)
   :`complete`:
       Complete tender lot (complete)
   :`cancelled`:
       Cancelled tender lot (cancelled)

   Status of the Lot.

Additionally in :ref:`esco`:

:minimalStepPercentage:
   float, required

  Minimum step increment of the energy service contract performance indicator during auction that is calculated on participant’s bid. Possible values: from 0.005 to 0.03 (from 0.5% to 3% respectively) with 3-digit precision after comma.

:fundingKind:
    string, required

:Lot funding source:

    Possible values:

    * budget -  Budget funding.
    * other - Supplier funding.

    Default value: other

:yearlyPaymentsPercentageRange:
    float, required

    Fixed percentage of participant's cost reduction sum, with 3-digit precision after comma.

    Possible values:

   * from 0.8 to 1 (from 80% to 100% respectively) if lot:fundingKind:other.
   * from 0 to 0.8 (from 0% to 80% respectively) if lot:fundingKind:budget.

     Input precision - 3 digits after comma.


Workflow in :ref:`limited`, :ref:`esco` and :ref:`openeu`
---------------------------------------------------------

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