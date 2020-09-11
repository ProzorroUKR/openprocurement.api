
.. _criteria_operation:

Tender Criteria
===============

Criteria Basic Operation
~~~~~~~~~~~~~~~~~~~~~~~~

Criteria data :ref:`schema<criterion>`

Criteria is part of tender documentation, so all operation with criteria make tender owner.

Create Tender Criteria
""""""""""""""""""""""

Criteria exist in procedures: belowThreshold, aboveThresholdUA, aboveThresholdEU,
competitiveDialogueUA, competitiveDialogueEU, competitiveDialogueUA.stage2,
competitiveDialogueEU.stage2, esco, closeFrameworkAgreementUA, closeFrameworkAgreementSelectionUA

You can create few criteria in one request with complete set of data.


.. include:: ../http/criteria/bulk-create-criteria.http
   :code:


Update Tender Criteria
""""""""""""""""""""""

.. include:: ../http/criteria/patch-criteria.http
   :code:


Get Tender Criteria
"""""""""""""""""""

.. include:: ../http/criteria/criteria-list.http
   :code:

.. include:: ../http/criteria/criteria.http
   :code:


Requirement Group basic operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requirement group :ref:`schema<RequirementGroup>`

Create Criteria Requirement Group
"""""""""""""""""""""""""""""""""

.. include:: ../http/criteria/add-criteria-requirement-group.http
   :code:


Update Criteria Requirement Group
"""""""""""""""""""""""""""""""""

.. include:: ../http/criteria/patch-criteria-requirement-group.http
   :code:

Get Criteria Requirement Group
""""""""""""""""""""""""""""""

.. include:: ../http/criteria/criteria-requirement-group-list.http
   :code:

.. include:: ../http/criteria/criteria-requirement-group.http
   :code:


Requirement basic operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requirement model :ref:`schema<requirement>`

Create Requirement
""""""""""""""""""

.. include:: ../http/criteria/add-criteria-requirement.http
   :code:


Update Requirement
""""""""""""""""""

.. include:: ../http/criteria/criteria-requirement-list.http
   :code:

.. include:: ../http/criteria/criteria-requirement.http
   :code:

Get Requirement
"""""""""""""""

.. include:: ../http/criteria/criteria-requirement.http
   :code:

Eligible Evidence basic operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Eligible Evidence model :ref:`schema<EligibleEvidence>`

Create Eligible Evidence
""""""""""""""""""""""""

.. include:: ../http/criteria/add-requirement-evidence.http
   :code:

Update Eligible Evidence
""""""""""""""""""""""""

.. include:: ../http/criteria/patch-requirement-evidence.http
   :code:

Delete Eligible Evidence
""""""""""""""""""""""""

.. include:: ../http/criteria/delete-requirement-evidence.http
   :code:


Retrieve Eligible Evidence
""""""""""""""""""""""""""

 .. include:: ../http/criteria/requirement-evidences-list.http
   :code:

.. include:: ../http/criteria/requirement-evidence.http
   :code:


Exclusion criteria
~~~~~~~~~~~~~~~~~~

Exclusion criteria available only on: aboveThresholdUA, aboveThresholdEU, competitiveDialogueUA,
competitiveDialogueEU, competitiveDialogueUA.stage2, competitiveDialogueEU.stage2, esco, closeFrameworkAgreementUA

Standard data, you could get `here <https://github.com/ProzorroUKR/standards/pull/79/files>`__

You can't update tender to status `active.tendering` without 9 EXCLUSION criteria:

.. include:: ../http/criteria/update-tender-status-without-criteria.http
   :code:

EXCLUSION criteria and all criteria objects are not updated:

.. include:: ../http/criteria/patch-exclusion-criteria.http
   :code:

.. include:: ../http/criteria/add-exclusion-criteria-requirement-group.http
   :code:

.. include:: ../http/criteria/patch-exclusion-criteria-requirement-group.http
   :code:

.. include:: ../http/criteria/add-exclusion-criteria-requirement.http
   :code:

.. include:: ../http/criteria/patch-exclusion-criteria-requirement.http
   :code:


.. _criteria_workflow:

Exclusion criteria workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. graphviz::

      digraph G {
        rankdir = LR


        tender_draft [
            label = "draft*"
            shape = circle
            fixedsize = true
            width = .9
        ]

        tender_active_tendering [
            label = "active.\ntendering"
            shape = circle
            fixedsize = true
            width = .9
        ]

        bid_draft [
            label = "draft"
            shape = circle
            fixedsize = true
            width = .9
        ]

        bid_active [
            label = "active"
            shape = circle
            fixedsize = true
            width = .9
        ]

        tender_draft -> tender_active_tendering;
        bid_draft -> bid_active;
        bid_active -> create_bid_object;

        create_requirement_response_object [
            label = "Create requirement \nresponses"
            shape = rect
            style = filled
            fillcolor = plum
            fixedsize = true
            height = .5
            width = 2
        ]
        create_bid_object [
            label = "Create bid"
            shape = rect
            style = filled
            fillcolor = moccasin
            fixedsize = true
            height = .25
            width = 2
        ]
        create_criteria_object [
            label = "Create Criteria\n(9 Exclusion criteria \nare required for \nsome procedures)"
            shape = rect
            style = filled
            fillcolor = lightsalmon
            fixedsize = true
            height = 1
            width = 2
        ]
        add_eligible_evidences_object [
            label = "Can be added \neligible evidences"
            shape = rect
            style = filled
            fillcolor = moccasin
            fixedsize = true
            height = .5
            width = 2
        ]

        block_patch_requirement_response_object [
            label = "Can't add or \nupdate requirement \nresponses and evidence"
            shape = rect
            style = filled
            fillcolor = moccasin
            fixedsize = true
            height = .75
            width = 2
        ]

        subgraph cluster_tender {
            label = "Tender"

            subgraph cluster_draft {
                label = ""
                style = filled
                color = plum
                tender_draft
                create_criteria_object
            }
            subgraph cluster_active {
                label = ""
                style = filled
                color = pink
                tender_active_tendering
                create_bid_object
                add_eligible_evidences_object
            }
        }
        subgraph cluster_bid {
            label = "Bid"

            subgraph cluster_draft {
                label = ""
                style = filled
                color = moccasin
                bid_draft
                create_requirement_response_object
            }
            subgraph cluster_active {
                label = ""
                style = filled
                color = mediumaquamarine
                bid_active
                block_patch_requirement_response_object
            }
        }
    }