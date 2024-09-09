.. _request_for_proposal:

requestForProposal
==================

Для розуміння структури компонентів коду системи з яких складається система і вимог до їх реалізації ознайомтесь з цим розілом документації:

- :ref:`cdb_structure`

План розробки та технічні вимоги до реалізації:
-----------------------------------------------

Фреймворк
~~~~~~~~~

1. Додати новий модуль openprocurement.framework.rfp (**requestForProposal**)

   1. Створити модуль openprocurement.framework.rfp (**requestForProposal**) аналогічний до openprocurement.framework.dps (**dynamicPurchasingSystem**)
   2. Створити нову схему конфігурації для openprocurement.framework.rfp **requestForProposal**
      https://github.com/ProzorroUKR/standards/tree/master/data_model/schema/FrameworkConfig

Тендер
~~~~~~

1. Перенесення бізнес логіки модуля openprocurement.tender.belowthreshold (**belowThreshold**) в модуль openprocurement.tender.core

   1. Перенести логіку стейт класів з модуля openprocurement.tenders.belowthreshold в модуль openprocurement.tenders.core
   2. Логіка має налаштовувтись атрибутами стейт класів (:ref:`приклад<cdb_state_classes>`)
   3. По замовчуванню за допомогою атрибутів стейт класів модуля openprocurement.tender.core перенесена логіка має бути вимкнена і не впливати на функціональність всіх модулів openprocurement.tender що наслідуються від  openprocurement.tender.core модуля
   4. Увімкнути перенесену логіку за допомогою перевизначення атрибутів стейт класів у модулі openprocurement.tender.core.belowthreshold

2. Додати новий модуль openprocurement.tender.rfp (**requestForProposal**)

   1. Створити модуль openprocurement.tender.rfp (**requestForProposal**) аналогічний до openprocurement.tender.belowthreshold (**belowThreshold**), в т.ч. мають бути аналогічні сутнісності:

      - models
      - state classes
      - views
      - tests
      - etc

   2. Налаштувати стейт класи нового модуля openprocurement.tender.rfp (**requestForProposal**) подібно до openprocurement.tender.belowthreshold (**belowThreshold**) але з особливостями нового типу процедури
   3. Створити нову схему конфігурації для openprocurement.tender.rfp (**requestForProposal**)
      https://github.com/ProzorroUKR/standards/tree/master/data_model/schema/TenderConfig
   4. Пересвідчитись в роботі hasPreSelectionAgreement конфігурації в openprocurement.tender.rfp (**requestForProposal**) або допрацювати/реалізувати її

3. Вимкнути в openprocurement.tender.belowthreshold (**belowThreshold**) функціональність що не відповідає новим вимогам цього типу процедури

   1. Налаштувати схему конфігурації openprocurement.tender.belowthreshold (**belowThreshold**) відповідно до нових обмежень процедури:
      https://github.com/ProzorroUKR/standards/blob/master/data_model/schema/TenderConfig/belowThreshold.json


Додаткова інформація
--------------------

Система ЦБД складається з наступних базових модулів:

- openprocurement.plan
- openprocurement.framework
- openprocurement.tender
- openprocurement.contracting
- openprocurement.relocation
- openprocurement.historical

.. note::
    Дана розробка стосується модуля **openprocurement.tender** та **openprocurement.framework**.

Фреймворк
~~~~~~~~~

Перелік модулів openprocurement.framework:

- openprocurement.framework.core
- openprocurement.framework.dps
- openprocurement.framework.electroniccatalogue
- openprocurement.framework.cfaua

.. note::
    Дана розробка передбачає створення нового модуля openprocurement.framework.rfp (**requestForProposal**) і не має вплинути на функціональність інших модулів openprocurement.framework


Тендер
~~~~~~

Перелік модулів openprocurement.tender:

- openprocurement.tender.core

- openprocurement.tender.belowthreshold

  - **belowThreshold**

- openprocurement.tender.open

  - **aboveThreshold**
  - **competitiveOrdering**

- openprocurement.tender.openua

  - **aboveThresholdUA**

- openprocurement.tender.openeu

  - **aboveThresholdEU**

- openprocurement.tender.openuadefense

  - **aboveThresholdUA.defense**

- openprocurement.tender.simpledefense

  - **simple.defense**

- openprocurement.tender.pricequotation

  - **priceQuotation**

- openprocurement.tender.limited

  - **reporting**
  - **negotiation**
  - **negotiation.quick**

- openprocurement.tender.esco

  - **esco**

- openprocurement.tender.competitivedialogue

  - **competitiveDialogueUA**
  - **competitiveDialogueEU**
  - **competitiveDialogueEU.stage2**
  - **competitiveDialogueUA.stage2**

- openprocurement.tender.cfaua

  - **closeFrameworkAgreementUA**

- openprocurement.tender.cfaselectionua

  - **closeFrameworkAgreementSelectionUA**

.. note::
    Дана розробка стосується модулів openprocurement.tender.core, openprocurement.tender.belowthreshold (**belowThreshold**) а також включає створення нового модуля openprocurement.tender.rfp (**requestForProposal**) і не має вплинути на функціональність інших модулів openprocurement.tender


Модуль openprocurement.tender.core:

https://github.com/ProzorroUKR/openprocurement.api/tree/master/src/openprocurement/tender/core

Перелік стейт класів модуля openprocurement.tender.core:

https://github.com/ProzorroUKR/openprocurement.api/tree/master/src/openprocurement/tender/core/procedure/state

- `TenderState`
- `TenderDetailsState`
- `TenderDocumentState`
- `TenderClaimState`
- `TenderComplaintState`
- `TenderQuestionState`
- `LotState`
- `CriterionState`
- `RequirementGroupState`
- `RequirementState`
- `EligibleEvidenceState`
- `ReviewRequestState`
- `ComplaintDocumentState`
- `ComplaintPostState`
- `ComplaintPostDocumentState`
- `BidState`
- `BidReqResponseState`
- `BidReqResponseEvidenceState`
- `QualificationState`
- `QualificationClaimState`
- `QualificationComplaintState`
- `QualificationComplaintDocumentState`
- `QualificationMilestoneState`
- `QualificationReqResponseState`
- `QualificationReqResponseEvidenceState`
- `AwardState`
- `AwardClaimState`
- `AwardComplaintState`
- `AwardComplaintDocumentState`
- `AwardDocumentState`
- `AwardReqResponseState`
- `AwardReqResponseEvidenceState`
- `ContractState`
- `ContractDocumentState`
- `CancellationState`
- `CancellationComplaintState`
- `CancellationComplaintDocumentState`
- `CancellationDocumentState`

Модуль openprocurement.tender.belowthreshold:

https://github.com/ProzorroUKR/openprocurement.api/tree/master/src/openprocurement/tender/belowthreshold

Перелік стейт класів модуля openprocurement.tender.belowthreshold**:

https://github.com/ProzorroUKR/openprocurement.api/tree/master/src/openprocurement/tender/belowthreshold/procedure/state

- `BelowThresholdTenderState`
- `BelowThresholdTenderDetailsState`
- `BelowThresholdTenderDocumentState`
- `BelowThresholdTenderClaimState`
- `BTComplaintDocumentState`
- `ReviewRequestState`
- `BelowThresholdBidState`
- `AwardState`
- `BelowThresholdAwardClaimState`
- `BTAwardComplaintDocumentState`
- `BelowThresholdContractState`
- `BelowThresholdCriterionState`
- `BelowThresholdRequirementGroupState`
- `BelowThresholdRequirementState`
- `BelowThresholdEligibleEvidenceState`
- `TenderLotState`
- `BelowThresholdTenderQuestionStateMixin`
- `BelowThresholdCancellationState`
- `BTCancellationDocumentState`

