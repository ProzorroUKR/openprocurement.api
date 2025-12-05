
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

    Possible string values are:

        * `rationaleTypes for LAW 922 <https://github.com/ProzorroUKR/standards/blob/e41d3747a90880d394c209b978ccaec9ad288755/codelists/contract_change_rationale_type_law_922.json>`_
        * `rationaleTypes for DECREE 1178 <https://github.com/ProzorroUKR/standards/blob/e41d3747a90880d394c209b978ccaec9ad288755/codelists/contract_change_rationale_type_decree_1178.json>`_
        * `rationaleTypes general <https://github.com/ProzorroUKR/standards/blob/e41d3747a90880d394c209b978ccaec9ad288755/codelists/contract_change_rationale_type.json>`_ (deprecated after date CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM)

:date:
    string, :ref:`date`, auto-generated

:dateSigned:
    string, :ref:`date`

    |ocdsDescription|
    The date when the change was signed. In the case of multiple signatures, the date of the last signature.

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
