
.. include:: defs.hrst

.. index:: Claim, dispute

.. _claim:

Claim
=========

Schema
------

:id:
    uid, auto-generated

:author:
    :ref:`Organization`, required

    Organization filing a claim (contactPoint - person, identification - organization that person represents).

:title:
    string, required

    Title of the claim.

:description:
    Description of the issue.

:date:
    string, :ref:`date`, auto-generated

    Date of posting.

:dateSubmitted:
    string, :ref:`date`, auto-generated

    Date when claim was submitted.

:dateAnswered:
    string, :ref:`date`, auto-generated

    Date when Procuring entity answered the claim.


:dateDecision:
    string, :ref:`date`, auto-generated

    Date of claim decision.

:dateCanceled:
    string, :ref:`date`, auto-generated

    Date of cancelling.

:status:
    string

    Possible values are:

    * `draft`
    * `claim`
    * `answered`
    * `invalid`
    * `declined`
    * `resolved`
    * `cancelled`

:type:
    string

    Possible values of type are:

    * `claim`

:resolution:
    string

    Resolution of Procuring entity.

:resolutionType:
    string

    Possible values of resolution type are:

    * `invalid`
    * `declined`
    * `resolved`

:satisfied:
    bool

    Claim is satisfied?

:decision:
    string

    Reviewer decision.

:cancellationReason:
    string

    Cancellation reason.

:documents:
    List of :ref:`ConfidentialDocument` objects

:relatedLot:
    string

    Id of related :ref:`lot`.

:tendererAction:
    string

    Tenderer action.

:tendererActionDate:
    string, :ref:`date`, auto-generated

    Date of tenderer action.


