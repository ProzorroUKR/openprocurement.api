
.. _criteria_operation:

Criteria Basic Operation
------------------------

Criteria data :ref:`schema<criterion>`

Criteria is part of tender documentation, so all operation with criteria make tender owner.

Create Tender Criteria
""""""""""""""""""""""

Criteria exist in procedures: belowThreshold, aboveThresholdUA, aboveThresholdEU,
competitiveDialogueUA, competitiveDialogueEU, competitiveDialogueUA.stage2,
competitiveDialogueEU.stage2, esco, closeFrameworkAgreementUA, closeFrameworkAgreementSelectionUA

Criteria can be related to tenderer, lot, item and tender.
You cannot cancel lot or item if there is at least one related criterion with requirement in `active` status.
To cancel lot or set item quantity to 0 you should set `cancelled` status to all active requirements in related criterion.

You can create few criteria in one request with complete set of data.


.. http:example:: http/criteria/bulk-create-criteria.http
   :code:


Update Tender Criteria
""""""""""""""""""""""

.. http:example:: http/criteria/patch-criteria.http
   :code:


Get Tender Criteria
"""""""""""""""""""

.. http:example:: http/criteria/criteria-list.http
   :code:

.. http:example:: http/criteria/criteria.http
   :code:


Requirement Group basic operation
---------------------------------

Requirement group :ref:`schema<RequirementGroup>`

Requirement group that's object that contain requirements,
and sets the rules for how to respond to requirements.

Inside requirement groups you must gave response to all requirements(that's mean gave response to requirement group).
If criterion have more than one requirement groups you must gave response only to one requirement group.
If you try to gave responses to few requirement groups system will be returned error.

:ref:`There you can see how it works on practice. <bid_activation_with_requirement_responses>`

Create Criteria Requirement Group
"""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/add-criteria-requirement-group.http
   :code:


Update Criteria Requirement Group
"""""""""""""""""""""""""""""""""

.. http:example:: http/criteria/patch-criteria-requirement-group.http
   :code:

Get Criteria Requirement Group
""""""""""""""""""""""""""""""

.. http:example:: http/criteria/criteria-requirement-group-list.http
   :code:

.. http:example:: http/criteria/criteria-requirement-group.http
   :code:


Requirement basic operation
---------------------------

Requirement model :ref:`schema<requirement>`

Create Requirement
""""""""""""""""""

.. http:example:: http/criteria/add-criteria-requirement.http
   :code:


Update Requirement
""""""""""""""""""
You can use PATCH method to update requirements for tenders in draft statuses.

.. http:example:: http/criteria/patch-criteria-requirement.http
   :code:

To update requirement in non-draft status of tender you should use PUT method.
New version with status `active` will be created.
Status of old version of requirement will be changed to `cancelled`.

.. http:example:: http/criteria/put-exclusion-criteria-requirement.http
   :code:

.. http:example:: http/criteria/criteria-requirement-list.http
   :code:

Delete Requirement
""""""""""""""""""
To delete requirement from requirement group you can set status `cancelled` to this requirement.

.. http:example:: http/criteria/criteria-requirement-cancellation.http
   :code:

Get Requirement
"""""""""""""""

.. http:example:: http/criteria/criteria-requirement-list.http
   :code:

.. http:example:: http/criteria/criteria-requirement.http
   :code:

Eligible Evidence basic operation
---------------------------------

Eligible Evidence model :ref:`schema<EligibleEvidence>`

Create Eligible Evidence
""""""""""""""""""""""""
You can use POST method to add evidence for tenders in draft statuses.

.. http:example:: http/criteria/add-requirement-evidence.http
   :code:

To add evidence(s) in non-draft status of tender you should use PUT method on Requirement level with extended eligibleEvidences array.
New version or Requirement with status `active` and with extended eligibleEvidences array will be created.

.. http:example:: http/criteria/requirement-put-add-evidence.http
   :code:

Update Eligible Evidence
""""""""""""""""""""""""
You can use PATCH method to update evidence for tenders in draft statuses.

.. http:example:: http/criteria/patch-requirement-evidence.http
   :code:

To update evidence(s) in non-draft status of tender you should use PUT method on Requirement level with updated evidence(s) in eligibleEvidences array.
New version or Requirement with status `active` and with changed eligibleEvidences array will be created.

.. http:example:: http/criteria/requirement-put-update-evidence.http
   :code:

Delete Eligible Evidence
""""""""""""""""""""""""
You can use DELETE method to delete evidence for tenders in draft statuses.

.. http:example:: http/criteria/delete-requirement-evidence.http
   :code:

For tenders in non-draft statuses evidence(s) can be deleted from Requirement only by using PUT method on Requirement level.
Use eligibleEvidences array without some evidence(s) to delete them from Requirement.
To delete all evidences from Requirement use empty array for eligibleEvidences field.

.. http:example:: http/criteria/requirement-put-delete-evidence.http
   :code:

For tenders in draft statuses there is possibility to create, update and delete eligibleEvidences, make PATCH request to requirement and send new list of `eligibleEvidences`:

.. http:example:: http/criteria/bulk-update-requirement-evidence.http
   :code:

.. http:example:: http/criteria/bulk-delete-requirement-evidence.http
   :code:

Retrieve Eligible Evidence
""""""""""""""""""""""""""

 .. http:example:: http/criteria/requirement-evidences-list.http
   :code:

.. http:example:: http/criteria/requirement-evidence.http
   :code:


Exclusion criteria
------------------

Exclusion criteria available and required for the following procedures: aboveThresholdUA, aboveThresholdEU, competitiveDialogueUA,
competitiveDialogueEU, competitiveDialogueUA.stage2, competitiveDialogueEU.stage2, esco, closeFrameworkAgreementUA

`Standard data, you could get here <https://github.com/ProzorroUKR/standards/blob/master/criteria/article_17.json>`__

You can't update tender to status `active.tendering` without 9 EXCLUSION and 1 OTHER.BID.LANGUAGE criteria:

.. http:example:: http/criteria/update-tender-status-without-criteria.http
   :code:

EXCLUSION criteria and all criteria objects are unchangeable:

.. http:example:: http/criteria/patch-exclusion-criteria.http
   :code:

.. http:example:: http/criteria/add-exclusion-criteria-requirement-group.http
   :code:

.. http:example:: http/criteria/patch-exclusion-criteria-requirement-group.http
   :code:

.. http:example:: http/criteria/add-exclusion-criteria-requirement.http
   :code:

For tenders in draft statuses you can patch exclusion requirement, but you can send only `eligibleEvidences`

.. http:example:: http/criteria/patch-exclusion-criteria-requirement.http
   :code:

For tenders in non-draft statuses you can PUT exclusion requirement, but you can change only `status` and `eligibleEvidences`

.. http:example:: http/criteria/put-exclusion-criteria-requirement.http
   :code:

Language criterion workflow
"""""""""""""""""""""""""""

Language criterion creates as other and could be presented in bulk request with other criteria. Language should be specified in `title`

.. http:example:: http-handwritten/criteria/create-language-criterion.http
   :code:

But field `eligibleEvidences` is forbidden

.. http:example:: http-handwritten/criteria/update-language-criterion-with-evidence.http
   :code:

`expectedValue` must be only true

.. http:example:: http-handwritten/criteria/update-language-criterion-with-not-listed-lang.http
   :code:

Bid guarantee criterion (available for tenders: `belowThreshold`, `aboveThresholdUA`, `aboveThresholdEU`, `esco`).
If specified, should be also specified `guarantee` for tender if criterion
`relatesTo` = `'tender'` or `guarantee` for lot if `relatesTo` = `'lot'`

.. http:example:: http-handwritten/criteria/create-bid-guarantee-criterion.http
   :code:

Contract guarantee criterion (available for tenders: `belowThreshold`, `aboveThresholdUA`, `aboveThresholdEU`, `esco`).
For current criterion could be set only `source` = `'winner'`.
`eligibleEvidences` could be added according to :ref:`bidding`

.. http:example:: http-handwritten/criteria/create-contract-guarantee-criterion.http
   :code:

.. _criteria_workflow:

Exclusion criteria workflow
"""""""""""""""""""""""""""

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
