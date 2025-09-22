.. _contract-template-name:


Providing contract template
===========================

For further contracting it is possible provide contract template. There are two ways to do this:

1. Upload ``contractProforma`` document.
2. Set ``contractTemplateName`` field.

If contract template is required it should be provided in `draft` status (before tender activation).

Next table shows which procurementMethodType requires contract template or for which it is optional:


+------------------------------------+------------------+
| procurementMethodType              | Support          |
+====================================+==================+
| belowThreshold                     | **Required**     |
+------------------------------------+------------------+
| aboveThresholdUA                   | **Required**     |
+------------------------------------+------------------+
| aboveThresholdEU                   | **Required**     |
+------------------------------------+------------------+
| aboveThreshold                     | **Required**     |
+------------------------------------+------------------+
| competitiveDialogueUA              | Optional         |
+------------------------------------+------------------+
| competitiveDialogueEU              | Optional         |
+------------------------------------+------------------+
| competitiveDialogueUA.stage2       | Automatically    |
+------------------------------------+------------------+
| competitiveDialogueEU.stage2       | Automatically    |
+------------------------------------+------------------+
| esco                               | Optional         |
+------------------------------------+------------------+
| priceQuatation                     | **Required**     |
+------------------------------------+------------------+
| closeFrameworkAgreementUA          | Optional         |
+------------------------------------+------------------+
| competitiveOrdering                | **Required**     |
+------------------------------------+------------------+
| negotiation                        | Optional         |
+------------------------------------+------------------+
| negotiation.quick                  | Optional         |
+------------------------------------+------------------+
| reporting                          | Not available    |
+------------------------------------+------------------+
| simple.defence                     | **Required**     |
+------------------------------------+------------------+
| closeFrameworkAgreementSelectionUA | Optional         |
+------------------------------------+------------------+
| requestForProposal                 | **Required**     |
+------------------------------------+------------------+

Uploading `contractProforma`
============================

Let's upload `contractProforma` document:

.. http:example:: ./http/contract-template-name/add-contract-proforma.http
   :code:

Setting `contractTemplateName`
==============================

Next table shows which statuses for each procurementMethodType allow to set/update `contractTemplateName`:

+------------------------------------+------------------------------------------+
| procurementMethodType              | Statuses                                 |
+====================================+==========================================+
| belowThreshold                     | draft/active.enquiries                   |
+------------------------------------+------------------------------------------+
| aboveThresholdUA                   | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| aboveThresholdEU                   | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| aboveThreshold                     | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| competitiveDialogueUA              | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| competitiveDialogueEU              | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| competitiveDialogueUA.stage2       |                                          |
+------------------------------------+------------------------------------------+
| competitiveDialogueEU.stage2       |                                          |
+------------------------------------+------------------------------------------+
| esco                               | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| priceQuatation                     | draft                                    |
+------------------------------------+------------------------------------------+
| closeFrameworkAgreementUA          | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| competitiveOrdering                | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| negotiation                        | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| negotiation.quick                  | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| reporting                          |                                          |
+------------------------------------+------------------------------------------+
| simple.defence                     | draft/active.tendering                   |
+------------------------------------+------------------------------------------+
| closeFrameworkAgreementSelectionUA | draft                                    |
+------------------------------------+------------------------------------------+
| requestForProposal                 | draft/active.enquiries/active.tendering  |
+------------------------------------+------------------------------------------+

The correctness of the `contractTemplateName` is determined by items classification id.

All available templates and their selection rules can be found in the `standards
<https://github.com/ProzorroUKR/standards/blob/master/templates/contract_templates.json>`_.

If you try to set value out from standards or invalid for current classification, you'll get error:

.. http:example:: ./http/contract-template-name/set-contract-template-name-invalid.http
   :code:

Let's try to set correct value for `contractTemplateName` field:

.. http:example:: ./http/contract-template-name/set-contract-template-name-success.http
   :code:

Also `contractTemplateName` can't be set together with uploaded `contractProforma` document:

.. http:example:: ./http/contract-template-name/invalid-with-contract-proforma.http
   :code:

If you try to set or change value in invalid tender status you'll get error:

.. http:example:: ./http/contract-template-name/set-contract-template-in-incorrect-statuese.http
   :code:

You can delete contract template while in `draft` tender status:

.. http:example:: ./http/contract-template-name/delete-contract-template-name.http
   :code:
