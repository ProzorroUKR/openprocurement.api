.. _constants:

Constants
=========

.. include:: tendering/http/tutorial/constants.http
   :code:

* **BUDGET_PERIOD_FROM** - Added `period` to planning `Budget` model and use instead of `year` field
* **NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM** - Made not required `additionalClassifications`
* **CPV_336_INN_FROM** - `additionalClassifications` have to have only one classification
* **ORGANIZATION_SCALE_FROM** - `scale` became required
* **VAT_FROM** - Readonly attributes for `valueAddedTaxIncluded`
* **MPC_REQUIRED_FROM** - `mainProcurementCategory` became required
* **MILESTONES_VALIDATION_FROM** - Added validations for `milestone`
* **PLAN_BUYERS_REQUIRED_FROM** - `buyers` became required
* **BUDGET_BREAKDOWN_REQUIRED_FROM** - Field `breakdown` became required for tenders ("belowThreshold", "reporting", "esco")
* **WORKING_DATE_ALLOW_MIDNIGHT_FROM** - Allowed working in midnight
* **NORMALIZED_CLARIFICATIONS_PERIOD_FROM** - normalized certifications period
* **QUICK_CAUSE_REQUIRED_FROM** - `cause` became required
* **RELEASE_2020_04_19** - New cancellation flow with complaints was implemented
* **VALIDATE_ADDRESS_FROM** - Validation for Address `countryName` and `region`
* **COMPLAINT_IDENTIFIER_REQUIRED_FROM** - `ComplaintIdentifier` became required
* **PLAN_ADDRESS_KIND_REQUIRED_FROM** - `kind` in `PlanAddress` became required
* **NEW_NEGOTIATION_CAUSES_FROM** - Implemented new cause choices for Negotiation procedure
* **NORMALIZED_TENDER_PERIOD_FROM** - normalized tender period
* **MINIMAL_STEP_VALIDATION_FROM** - Added validation for `minimalStep`
* **RELEASE_ECRITERIA_ARTICLE_17** - Criteria was implemented
* **CRITERION_REQUIREMENT_STATUSES_FROM** - Implemented statuses to criterion requirement
* **RELEASE_SIMPLE_DEFENSE_FROM** - New defense procedure
* **NEW_DEFENSE_COMPLAINTS_FROM** - New defence complaints supports from date
* **NEW_DEFENSE_COMPLAINTS_TO** - New defence complaints supports to date
* **NO_DEFENSE_AWARD_CLAIMS_FROM** - Complaint type is should be only "complaint"
