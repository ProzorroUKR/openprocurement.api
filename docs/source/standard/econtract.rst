
.. include:: defs.hrst

.. index:: EContract
.. _EContract:

EContract
=========

Schema
------

:id:
    uid, auto-generated

    |ocdsDescription|
    The identifier for this contract.

:awardID:
    string, required

    |ocdsDescription|
    The `Award.id` against which this contract is being issued.

:contractID:
    string, auto-generated, read-only

:contractNumber:
    string

:title:
    string, required

    |ocdsDescription|
    Contract title

:description:
    string

    |ocdsDescription|
    Contract description

:status:
    string, required

    |ocdsDescription|
    The current status of the contract.

    Possible values are:

    * `pending` - this contract has been proposed, but is not yet in force.
      It may be awaiting signature.
    * `active` - this contract has been signed by all the parties, and is
      now legally in force.
    * `cancelled` - this contract has been cancelled prior to being signed.

    * `terminated` - this contract was signed and in force, and has now come
      to a close.  This may be due to a successful completion of the contract,
      or may be early termination due to some non-completion issue.

:period:
    :ref:`Period`

    |ocdsDescription|
    The start and end date for the contract.

:items:
    List of :ref:`Item` objects, auto-generated, read-only

    |ocdsDescription|
    The goods, services, and any intangible outcomes in this contract. Note: If the items are the same as the award do not repeat.

:suppliers:
    List of :ref:`EContractOrganization` objects, auto-generated, read-only

:value:
    :ref:`ContractValue` object, auto-generated

    |ocdsDescription|
    The total value of this contract.

    Check ":ref:`SettingContractValue`" tutorial section for more info

:dateSigned:
    string, :ref:`date`

    |ocdsDescription|
    The date when the contract was signed. In the case of multiple signatures, the date of the last signature.


:documents:
    List of :ref:`Document` objects

    |ocdsDescription|
    All documents and attachments related to the contract, including any notices.


:buyer:
   :ref:`EContractOrganization`

   |ocdsDescription|
   The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.


:changes:
    List of :ref:`Change` objects.

:amountPaid:

    :amount: float, required
    :currency: string, required, auto-generated
    :valueAddedTaxIncluded: bool, required , auto-generated

    Amount of money actually paid.

:implementation:
    :ref:`Implementation`

:terminationDetails:
    string, required for unsuccessful contract

    Reasons for contract termination. Presence of this field indicates that contract is unsuccessful.

:contractTemplateUri:
    string, auto-generated

    template link on standards


Workflow
--------

.. graphviz::

    digraph G {
        A [ label="pending*" ]
        B [ label="active" ]
        C [ label="cancelled" ]
        D [ label="terminated"]
         A -> B;
         A -> C [label="on Award cancellation or contract set status"] ;
         B -> D;
    }

\* marks initial state
