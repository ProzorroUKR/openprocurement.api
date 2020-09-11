

.. index:: Bid, Parameter, LotValue, bidder, participant, pretendent

.. _bid:

Bid
===

Schema
------

:tenderers:
    List of :ref:`BusinessOrganization` objects

:date:
    string, :ref:`date`, auto-generated

:id:
    uid, auto-generated

:status:
    string

    Possible values are:

    * `draft`
    * `active`

    Possible values in :ref:`defense` and :ref:`openua`:

    * `draft`
    * `active`
    * `invalid`
    * `deleted`

    Possible values in :ref:`openeu` and :ref:`esco`:

    * `draft`
    * `pending`
    * `active`
    * `invalid`
    * `invalid.pre-qualification`
    * `deleted`

    Possible values in :ref:`competitivedialogue`:

    * `draft`
    * `pending`
    * `active`
    * `invalid`
    * `deleted`

:value:
    :ref:`Value`, required

    Validation rules:

    * `amount` should be less than `Tender.value.amount`
    * `currency` should either be absent or match `Tender.value.currency`
    * `valueAddedTaxIncluded` should either be absent or match `Tender.value.valueAddedTaxIncluded`

:documents:
    List of :ref:`Document` objects

    Differences in :ref:`competitivedialogue`, :ref:`cfaua`, :ref:`openeu`, :ref:`openua`, :ref:`defense` and :ref:`esco`:

        List of :ref:`ConfidentialDocument` objects. See :ref:`confidential-documents`

:parameters:
    List of :ref:`Parameter` objects

:lotValues:
    List of :ref:`LotValue` objects

:participationUrl:
    url

    A web address for participation in auction.

Additionally in :ref:`defense`, :ref:`openua`, :ref:`openeu`, :ref:`esco` and :ref:`competitivedialogue`:

    :selfEligible':
        True, required

        Confirms compliance of eligibility criteria set by the procuring entity in the tendering documents.

    :selfQualified:
        True, required

        Confirms the absence of grounds for refusal to participate in accordance with Article 17 of the Law of Ukraine "On Public Procurement".

    :subcontractingDetails:
        string

        While submitting bid proposal, participant can fill in the text field of any length about subcontractor.


There are additional `envelopes` - document containers that manage time when their information will be revealed in :ref:`openeu` and :ref:`esco`:

    :financialDocuments:
        List of :ref:`ConfidentialDocument` objects. This envelope can contain financial part of proposal (`commercialProposal` and `billOfQuantity`). It is revealed at post-qualification.

    :eligibilityDocuments:
        List of :ref:`ConfidentialDocument` objects. This envelope can contain `eligibilityDocuments` document type. It is revealed at pre-qualification.

    :qualificationDocuments:
        List of :ref:`ConfidentialDocument` objects. This envelope is revealed at post-qualification.

    :requirementResponses:
        List of :ref:`RequirementResponse` objects.

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


:participationUrl:
    url

    A web address for participation in auction.


Additionally in :ref:`defense`, :ref:`openua`, :ref:`openeu` and :ref:`competitivedialogue`:

:subcontractingDetails:
    string

    While submitting bid proposal, participant can fill in the text field of any length about subcontractor.



Workflow in :ref:`openeu`, :ref:`esco` and :ref:`competitivedialogue`
---------------------------------------------------------------------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active"]
        C [ label="cancelled"]
        D [ label="unsuccessful"]
        E [ label="deleted"]
        F [ label="invalid"]
         A -> B [dir="both"];
         A -> C;
         A -> D [dir="both"];
         A -> E;
         A -> F [dir="both"];
         B -> C;
         D -> C;
         E -> C;
         F -> C;
         F -> E;
    }

\* marks initial state
