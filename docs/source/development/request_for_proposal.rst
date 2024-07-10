.. _request_for_proposal:

requestForProposal
==================

Для розуміння структури компонентів коду системи з яких складається система і вимог до їх реалізації ознайомтесь з цим розілом документації:

- :ref:`developers_structure`

Додаткова інформація
--------------------

Система ЦБД складається з наступних базових модулів:

- plan
- framework
- tender
- contracting
- relocation
- historical

.. note::
    Дана розробка стосується модуля **tender**.

Перелік модулів модуля тендерінгу:

- core
- belowthreshold (**belowThreshold**)
- open (**aboveThreshold**, **competitiveOrdering**)
- openua (**aboveThresholdUA**)
- openeu (**aboveThresholdEU**)
- openuadefense (**aboveThresholdUA.defense**)
- simpledefense (**simple.defense**)
- pricequotation (**priceQuotation**)
- limited (**reporting**, **negotiation**, **negotiation.quick**)
- esco (**esco**)
- competitivedialogue (**competitiveDialogueUA**, **competitiveDialogueEU**, **competitiveDialogueEU.stage2**, **competitiveDialogueUA.stage2**)
- cfaua (**closeFrameworkAgreementUA**)
- cfaselectionua (**closeFrameworkAgreementSelectionUA**)

.. note::
    Дана розробка стосується модулів core, belowthreshold (**belowThreshold**) а також включає створення нового модуля для **requestForProposal**.


Модуль **core** модуля тендерінгу:

https://github.com/ProzorroUKR/openprocurement.api/tree/master/src/openprocurement/tender/core

Перелік стейт класів **core** модуля тендерінгу:

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

Модуль **belowthreshold** модуля тендерінгу:

https://github.com/ProzorroUKR/openprocurement.api/tree/master/src/openprocurement/tender/belowthreshold

Перелік стейт класів **belowthreshold** модуля тендерінгу:

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

План розробки та технічні вимоги до **requestForProposal**:
-----------------------------------------------------------

1. Перенесення бізнес логіки процедури **belowThreshold** в **core** модуль

   1. Перенести логіку стейт класів з модуля `openprocurement.tenders.belowthreshold` в модуль `openprocurement.tenders.core`
   2. Логіка має налаштовувтись атрибутами стейт класів
   3. По замовчуванню за допомогою атрибутів core стейт класів перенесена логіка має бути вимкнена і не впливати на функціональність всіх модулів тендерінгу що наслідуються від **core** модуля
   4. Увімкнути перенесену логіку за допомогою перевизначення атрибутів стейт класів у **belowThreshold**

2. Додати новий модуль для процедури **requestForProposal**

   1. Зробити копію **belowThreshold** модуль змінивши назву процедури на **requestForProposal**, в т.ч.:

      - Models
      - StateClasses
      - Views
      - Tests
      - etc

   2. Налаштувати стейт класи нового модуля подібно до **belowThreshold** але з особливостями нової процедури якщо такі є
   3. Створити нову схему конфігурації для нового типу процедури **requestForProposal**:
      https://github.com/ProzorroUKR/standards/tree/master/data_model/schema/TenderConfig

3. Вимкнути в **belowThreshold** функціональність що не відповідає новим вимогам цього типу процедури

   1. Налаштувати схему конфігурації відповідно до нових обмежень процедури:
      https://github.com/ProzorroUKR/standards/blob/master/data_model/schema/TenderConfig/belowThreshold.json
