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

:guarantee:
    :ref:`Guarantee`

    Bid guarantee

:minimalStepPercentage:
   float, required

  Minimum step increment of the energy service contract performance indicator during auction that is calculated on participant’s bid. Possible values: from 0.05 to 0.3 (from 0.5% to 3% respectively) with 3-digit precision after comma.

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
   
:fundingKind:
    string, required
    
:Lot funding source:
      Possible values:
       
       *budget -  Budget funding.
       *other - Supplier funding.
    
    Default value: other
    
:yearlyPaymentsPercentageRange:
    float, required

     Fixed percentage of participant's cost reduction sum, with 3-digit precision after comma.

     Possible values:
     
     *from 0.8 to 1 (from 80% to 100% respectively) if lot:fundingKind:other. Default value.
     *from 0 to 0.8 (from 0% to 80% respectively) if lot:fundingKind:budget.

     Input precision - 3 digits after comma.


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
