.. . Kicking page rebuild 2014-10-30 17:00:08

.. index:: Bid, Parameter, LotValue, bidder, participant, pretendent

.. _bid:

Bid
===

Schema
------

:tenderers:
    List of :ref:`Organization` objects

:date:
    string, :ref:`date`, auto-generated

:id:
    uid, auto-generated

:status:
    string

    Possible values are:
    
    * `draft`
    * `active`
    * `invalid`
    * `deleted`

:value:
    :ref:`Value`, required

    Validation rules:

    * `amount` should be less than `Tender.value.amout`
    * `currency` should either be absent or match `Tender.value.currency`
    * `valueAddedTaxIncluded` should either be absent or match `Tender.value.valueAddedTaxIncluded`

:selfEligible:
    True, required

    Confirms compliance of eligibility criteria set by the procuring entity in the tendering documents.

:selfQualified:
    True, required

    Confirms the absence of grounds for refusal to participate in accordance with Article 17 of the Law of Ukraine "On Public Procurement".

:subcontractingDetails:
    string

    When submitting proposals, participant can fill in the text field of any length about subcontractor.

:documents:
    List of :ref:`Document` objects

:parameters:
    List of :ref:`Parameter` objects

:lotValues:
    List of :ref:`LotValue` objects

:participationUrl:
    url

    A web address for participation in auction.

.. _Parameter:

Parameter
=========

Schema
------

:code:
    string, required

    Code of the feature.

:value:
    float, required

    Value of the feature.

.. _LotValue:

LotValue
========

Schema
------

:value:
    :ref:`Value`, required

    Validation rules:

    * `amount` should be less than `Lot.value.amout`
    * `currency` should either be absent or match `Lot.value.currency`
    * `valueAddedTaxIncluded` should either be absent or match `Lot.value.valueAddedTaxIncluded`

:relatedLot:
    string

    Id of related :ref:`lot`.

:date:
    string, :ref:`date`, auto-generated

:subcontractingDetails:
    string

    When submitting proposals, participant can fill in the text field of any length about subcontractor.

:participationUrl:
    url

    A web address for participation in auction.
