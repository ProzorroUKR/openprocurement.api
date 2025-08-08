
.. include:: defs.hrst


.. _EContractChange:

EContractChange
================

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

:status:
    string, required

    The current status of the change.

    Possible values are:

    * `pending` - this change has been added.

    * `active` - this change has been confirmed.

    * `cancelled` - this change has been cancelled.

:modifications:
    List of :ref:`EContractModifications` objects

    All fields of contract that will be modified after change is applied.

:documents:
    List of :ref:`ConfidentialDocument` objects

    All documents (signatures) related to the cancellation.

:cancellations:
   List of :ref:`EContractCancellation` objects.

   Contains 1 object with `active` status in case of cancelled change.

   The :ref:`EContractCancellation` object describes the reason of change cancellation.

:author:
    string, auto-generated

    The author of change

.. _EContractModifications:

ContractModifications
=====================

Schema
------

:title:
    string, required

    |ocdsDescription|
    Contract title

:description:
    string

    |ocdsDescription|
    Contract description

:period:
    :ref:`Period`

    |ocdsDescription|
    The start and end date for the contract.

:value:
    :ref:`ContractValue` object, auto-generated

    |ocdsDescription|
    The total value of this contract.

    Check ":ref:`SettingContractValue`" tutorial section for more info

:items:
    List of :ref:`Item` objects, auto-generated, read-only

    |ocdsDescription|
    The goods, services, and any intangible outcomes in this contract. Note: If the items are the same as the award do not repeat.

:contractNumber:
    string
