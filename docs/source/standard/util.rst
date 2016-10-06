.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Period, startDate, endDate
.. _period:

Period
======

Schema
------

:startDate:
    string, :ref:`date`

    |ocdsDescription|
    The start date for the period.

:endDate:
    string, :ref:`date`, required 

    |ocdsDescription|
    The end date for the period.

`startDate` should always precede `endDate`.

.. _Date:

Date
====

Date/time in :ref:`date-format`.

.. index:: Value, Currency, VAT
.. _value:

Value
=====

Schema
------

:amount:
    float, required

    |ocdsDescription|
    Amount as a number.

    Should be positive.

:currency:
    string, required

    |ocdsDescription|
    The currency in 3-letter ISO 4217 format.

:valueAddedTaxIncluded:
    bool, required


.. _Change:
    
Change
======

Schema
------

:id:
    uid, auto-generated
    
    The identifier for this Change.

:rationale:
    string, multilingual, required
    
    Reason for contract change

:rationaleTypes:
    List of strings, required

    Type of the rationale behind contract change
    
    Changes to the contract can be made in cases described in the 4th part of Article 36 of the Law “On the Public Procurement”.
    
    Possible string values are:

    * `volumeCuts` - Reduction of the procurement’s volume
    
      reduction of the procurement’s volume, particularly taking into account the actual expenditures of the procuring entity;

    * `itemPriceVariation` - Change in the unit’s price
    
      change in the unit’s price (no more than 10%) due to product’s price fluctuations on the market, provided that the said change will not increase the sum of money specified in the contract;

    * `qualityImprovement` - Improvement of the procurement item’s quality
    
      improvement of the item's quality, provided that such improvement will not increase the sum of money specified in the contract;

    * `durationExtension` - Extension of the period of the contract duration (due to documented objective circumstances)
    
      extension of the period of the contract duration and obligations fulfilment regarding the transfer of goods, implementation of works and provision of services in case of documented objective circumstances that led to such extension, including force majeure, delays in funding of procuring entity’s  expenditures, provided that such changes will not increase the sum of money specified in the contract;

    * `priceReduction` - Coordinated price reduction
    
      coordinated downward price change (without changing the quantity (volume) and quality of goods, works, and services);

    * `taxRate` - Price changes due to changes in tax rates and fees
    
      price changes due to changes in tax rates and fees in proportion to changes of those rates;

    * `thirdParty` - Change of the third-party indicators (rate, indices...)
    
      changes of established under the law by the State Statistics Service consumer price index, changes in foreign currency, changes in stock prices or Platts indices, regulated prices (rates) and standards that are used in the procurement contract if the price change order is specified in the procurement contract;

    * `fiscalYearExtension` - Extension of the period of the contract duration to the next year
    
      changes in contract terms according to the provisions of part 5 of Article 36.

      Article 36 Part 5. Effect of the procurement contract may be continued for a period sufficient for conduction of the procurement procedure at the beginning of the next year in volume that does not exceed 20% of the sum specified in the contract concluded in the previous year, if expenditures for this purpose are approved in the prescribed manner.

:date:
    string, :ref:`date`, auto-generated

:dateSigned:
    string, :ref:`date`

:contractNumber:
    string

:status:
    string, required

    The current status of the change.

    Possible values are:

    * `pending` - this change has been added.
    * `active` - this change has been confirmed.

Workflow
--------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
         A -> B;
    }

\* marks initial state
