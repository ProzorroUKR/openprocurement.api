
.. _contract-template-name:


Contract template
=================

Supported procedures
--------------------

The contract template can be set for procedures and their statuses specified below in the table:


.. list-table:: Procedures supported
   :widths: 50 50
   :header-rows: 1

   * - Procedure type
     - Statuses
   * - belowThreshold
     - draft/active.enquiries
   * - aboveThresholdUA
     - draft/active.tendering
   * - aboveThresholdEU
     - draft/active.tendering
   * - aboveThreshold
     - draft/active.tendering
   * - competitiveDialogueUA
     - draft/active.tendering
   * - competitiveDialogueEU
     - draft/active.tendering
   * - competitiveDialogueUA.stage2
     - Automatically carried over from the first stage.
   * - competitiveDialogueEU.stage2
     - Automatically carried over from the first stage.
   * - esco
     - draft/active.tendering
   * - priceQuatation
     - draft(*required - without contractProforma document)
   * - closeFrameworkAgreementUA
     - draft/active.tendering
   * - competitiveOrdering
     - draft/active.tendering
   * - negotiation
     - draft/active.tendering
   * - negotiation.quick
     - draft/active.tendering
   * - reporting
     - -
   * - simple.defence
     - draft/active.tendering
   * - closeFrameworkAgreementSelectionUA
     - draft


Tutorial
--------

The correctness of the template is determined by items classification id.


All available templates and their selection rules can be found in the `standards
<https://github.com/ProzorroUKR/standards/blob/master/templates/contract_templates_keys.json>`_.

If you try to set value out from standards or invalid for current classification, you'll get error:

.. http:example:: ./http/contract-template-name/set-contract-template-name-invalid.http
   :code:

Also contract template can't be set together with `contractProforma` document:

.. http:example:: ./http/contract-template-name/add-contract-proforma.http
   :code:

.. http:example:: ./http/contract-template-name/invalid-with-contract-proforma.http
   :code:


Let's try to set correct value:

.. http:example:: ./http/contract-template-name/set-contract-template-name-success.http
   :code:

You can delete contract template:

.. http:example:: ./http/contract-template-name/delete-contract-template-name.http
   :code:

If you try to set or cnage value in invalid tender status you'll get error:

.. http:example:: ./http/contract-template-name/set-contract-template-in-incorrect-statuese.http
   :code:
