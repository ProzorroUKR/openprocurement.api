from typing import Any, Literal

from pydantic import Field, computed_field, field_validator

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.models.base import (
    Model,
    model_field_validator,
    validate_object_id_uniq,
    validate_uniq_id,
)
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.tender.competitivedialogue.procedure.models.item import CDItem
from openprocurement.tender.core.procedure.models.criterion import Criterion
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender,
    PostTender,
    Tender,
    validate_cd_shortlisted_firm_ids,
)


class CDStage1EUPostTender(PostTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_EU] = (  # type: ignore[valid-type]
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU
    )


class CDStage1EUPatchTender(PatchTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_EU] | None = None  # type: ignore[valid-type]


class CDStage1EUTender(Tender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_EU]  # type: ignore[valid-type]
    stage2TenderID: str | None = None


class CDStage1UAPostTender(CDStage1EUPostTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_UA] = (  # type: ignore[valid-type]
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA
    )


class CDStage1UAPatchTender(CDStage1EUPatchTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_UA] | None = None  # type: ignore[valid-type]


class CDStage1UATender(CDStage1EUTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_UA]  # type: ignore[valid-type]


class CDStage2LotId(Model):
    id: str | None = None


class CDStage2Firm(Model):
    identifier: Identifier
    name: str
    lots: list[CDStage2LotId] | None = None


class CDStage2EUPostTender(PostTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2] = (  # type: ignore[valid-type]
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2
    )
    owner: str
    # the number of the first stage tender with ".2" (the input), the output is `tenderID` (not generated)
    stage2_tender_id: str | None = Field(None, alias="tenderID", exclude=True)
    dialogue_token: str
    dialogueID: str | None = None
    shortlistedFirms: list[CDStage2Firm] = Field(min_length=3)
    items: list[CDItem] = Field(min_length=1)
    tenderPeriod: PeriodEndRequired | None = None
    criteria: list[Criterion] | None = None

    @computed_field
    def tenderID(self) -> Any:
        return self.stage2_tender_id

    @model_field_validator("shortlistedFirms")
    def validate_shortlisted_firms(self, value):
        validate_cd_shortlisted_firm_ids(self, value)

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("criteria")
    @classmethod
    def validate_criteria_items(cls, value):
        validate_object_id_uniq(value)
        return value


class CDStage2EUPatchTender(PatchTender):
    procurementMethodType: (  # type: ignore[valid-type]
        Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2] | None
    ) = None
    items: list[CDItem] | None = Field(None, min_length=1)

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value


class CDStage2EUTender(Tender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2]  # type: ignore[valid-type]
    dialogue_token: str
    dialogueID: str | None = None
    items: list[CDItem] = Field(min_length=1)
    shortlistedFirms: list[CDStage2Firm] = Field(min_length=3)

    @model_field_validator("shortlistedFirms")
    def validate_shortlisted_firms(self, value):
        validate_cd_shortlisted_firm_ids(self, value)

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value


class CDStage2UAPostTender(CDStage2EUPostTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2] = (  # type: ignore[valid-type]
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2
    )


class CDStage2UAPatchTender(CDStage2EUPatchTender):
    procurementMethodType: (  # type: ignore[valid-type]
        Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2] | None
    ) = None


class CDStage2UATender(CDStage2EUTender):
    procurementMethodType: Literal[ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2]  # type: ignore[valid-type]
