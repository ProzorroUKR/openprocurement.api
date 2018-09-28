.. include:: defs.hrst

.. _ChangeTaxRate:

ChangeTaxRate
======

Schema
------

.. include:: base_change.rst

:rationaleType:
    string

     Default value is `taxRate`.

:modifications:
    List of :ref:`UnitPriceModification` objects


.. _ChangeItemPriceVariation:

ChangeItemPriceVariation
======

Schema
------

.. include:: base_change.rst

:rationaleType:
    string

     Default value is `itemPriceVariation`.

:modifications:
    List of :ref:`UnitPriceModification` objects

.. _ChangeThirdParty:

ChangeThirdParty
======

Schema
------

.. include:: base_change.rst

:rationaleType:
    string

     Default value is `thirdParty`.

:modifications:
    List of :ref:`UnitPriceModification` objects


.. _ChangePartyWithdrawal:

ChangePartyWithdrawal
======

Schema
------

.. include:: base_change.rst

:rationaleType:
    string

     Default value is `partyWithdrawal`.

:modifications:
    List of :ref:`ContractModification` objects


.. _UnitPriceModification:

UnitPriceModification
======

Schema
------

:itemId:
    string

     Id of changing item.

:factor:
    decimal

     Min value is 0.0 .

:addend:
    decimal

     Is absolute value of changing.
     Note: factor and addend are not required fields. But one of fields should be provided.


.. _ContractModification:

ContractModification
======

Schema
------

:itemId:
    string

     Id of changing item.

:contractId:
    string, required

     Min value is 0.0 .


Workflow
--------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* marks initial state

