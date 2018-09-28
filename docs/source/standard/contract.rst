.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Contract
.. _Contract:

Contract
========

Schema
------

:id:
    uid, auto-generated

    |ocdsDescription|
    The identifier for this contract.

:awardID:
    string

    |ocdsDescription|
    The `Award.id` against which this contract is being issued.

:bidID:
    string

    |ocdsDescription|
    The `Bid.id` against which this contract is being issued.

:status:
    string

    |ocdsDescription|
    The current status of the contract.

    Possible values are:

    * `active` - this contract has been signed by all the parties, and is
      now legally in force.
    * `unsuccessful` - this contract was signed and in force, and has now come
      to a close.  This may be due to a successful completion of the contract,
      or may be early termination due to some non-completion issue.

:suppliers:
    List of :ref:`Organization` objects, auto-generated, read-only

:unitPrices:
    List of :ref:`UnitPrice` objects, auto-generated, read-only

:parameters:
    List of :ref:`Parameter` objects, auto-generated, read-only




Workflow
--------

.. graphviz::

    digraph G {
        A [ label="active*" ]
        B [ label="unsuccessful"]
         A -> B;
    }

\* marks initial state
