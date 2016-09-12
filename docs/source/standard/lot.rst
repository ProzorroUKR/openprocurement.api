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
