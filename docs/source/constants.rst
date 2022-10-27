.. _constants:

Constants
=========

.. http:example:: tendering/belowthreshold/http/tutorial/constants.http
   :code:

.. _BUDGET_PERIOD_FROM:

BUDGET_PERIOD_FROM
""""""""""""""""""
:ref:`Plan` :ref:`Budget` `year` deprecated in flavor of `period`

    For **plans** created starting the date specified in this constant use `period` instead of `year` in :ref:`Budget` of :ref:`Plan`

    .. note::

        For tender created **before** that date in case of attempt to provide period next error will be returned during :ref:`Budget` validation:

        .. code-block:: none

            Can't use period field, use year field instead

        For tender created **after** that date in case of attempt to provide year next error will be returned during :ref:`Budget` validation:

        .. code-block:: none

            Can't use year field, use period field instead

.. _NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM:

NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM
"""""""""""""""""""""""""""""""""""""""""""
Set non required `additionalClassifications` of :ref:`Item` with `classification` that have `id` **99999999-9**

    For **plans** and **tenders** created starting the date specified in this constant `additionalClassifications` of :ref:`Item` is not required if :ref:`Item` contains `classification` that have `id` **99999999-9**

.. _CPV_336_INN_FROM:

CPV_336_INN_FROM
""""""""""""""""
Validate INN `additionalClassifications` of :ref:`Item` with `classification` that have `id` **33600000-6**

    For **tenders** created starting the date specified in this constant `additionalClassifications` of :ref:`Item` has additional validations if :ref:`Item` contains `classification` that have `id` **33600000-6**

    .. note::

        Next validation errors are possible during :ref:`Item` validation:

        .. code-block:: none

            Item with classification.id=33600000-6 have to contain exactly one additionalClassifications with scheme=INN

        .. code-block:: none

            Item with classification.id that starts with 336 and contains additionalClassification objects have to contain no more than one additionalClassifications with scheme=INN

.. _ORGANIZATION_SCALE_FROM:

ORGANIZATION_SCALE_FROM
"""""""""""""""""""""""
Make `scale` field of :ref:`BusinessOrganization` required

.. _MPC_REQUIRED_FROM:

MPC_REQUIRED_FROM
"""""""""""""""""
Make `mainProcurementCategory` field of :ref:`Tender` required

.. _MILESTONES_VALIDATION_FROM:

MILESTONES_VALIDATION_FROM
""""""""""""""""""""""""""
Make `milestones` field of :ref:`Tender` required

.. _PLAN_BUYERS_REQUIRED_FROM:

PLAN_BUYERS_REQUIRED_FROM
"""""""""""""""""""""""""
Make `buyers` field of :ref:`Plan` required

BUDGET_BREAKDOWN_REQUIRED_FROM
""""""""""""""""""""""""""""""
Make `breakdown` field of :ref:`Tender` `budget` required for (`belowThreshold`, `reporting`, `esco`)

WORKING_DATE_ALLOW_MIDNIGHT_FROM
""""""""""""""""""""""""""""""""
Allow midnight (00:00) as valid boundary date for calculating periods

NORMALIZED_CLARIFICATIONS_PERIOD_FROM
"""""""""""""""""""""""""""""""""""""
Make dates for clarifications period normalized

QUICK_CAUSE_REQUIRED_FROM
"""""""""""""""""""""""""
Make `cause` field of :ref:`Tender` required for `quick` procedures

RELEASE_2020_04_19
""""""""""""""""""
New complaints and cancellation flow

VALIDATE_ADDRESS_FROM
"""""""""""""""""""""
Validation for :ref:`Address` `countryName` and `region` fields

COMPLAINT_IDENTIFIER_REQUIRED_FROM
""""""""""""""""""""""""""""""""""
`ComplaintIdentifier` became required

PLAN_ADDRESS_KIND_REQUIRED_FROM
"""""""""""""""""""""""""""""""
Make `kind` in `PlanAddress` required

NEW_NEGOTIATION_CAUSES_FROM
"""""""""""""""""""""""""""
Implemented new cause choices for `negotiation` procedure

NORMALIZED_TENDER_PERIOD_FROM
"""""""""""""""""""""""""""""
Make dates for periods normalized

MINIMAL_STEP_VALIDATION_FROM
""""""""""""""""""""""""""""
Added validation for `minimalStep`

RELEASE_ECRITERIA_ARTICLE_17
""""""""""""""""""""""""""""
Criteria was implemented

CRITERION_REQUIREMENT_STATUSES_FROM
"""""""""""""""""""""""""""""""""""
Implemented statuses to criterion requirement

RELEASE_SIMPLE_DEFENSE_FROM
"""""""""""""""""""""""""""
New defense procedure

NEW_DEFENSE_COMPLAINTS_FROM
"""""""""""""""""""""""""""
New defence complaints supports from date

NEW_DEFENSE_COMPLAINTS_TO
"""""""""""""""""""""""""
New defence complaints supports to date

NO_DEFENSE_AWARD_CLAIMS_FROM
""""""""""""""""""""""""""""
:ref:`Complaint` type should be only `complaint` for `defence` procedure

RELEASE_GUARANTEE_CRITERION_FROM
""""""""""""""""""""""""""""""""

RELEASE_METRICS_FROM
""""""""""""""""""""

VALIDATE_TELEPHONE_FROM
"""""""""""""""""""""""

REQUIRED_FIELDS_BY_SUBMISSION_FROM
""""""""""""""""""""""""""""""""""

VALIDATE_CURRENCY_FROM
""""""""""""""""""""""

UNIT_PRICE_REQUIRED_FROM
""""""""""""""""""""""""

MULTI_CONTRACTS_REQUIRED_FROM
"""""""""""""""""""""""""""""
Implemented creation of aggregate contracts. Look at `centralized-procurements` source.
