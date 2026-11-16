from typing import Annotated, Any, Literal

from pydantic import Field, computed_field, field_validator

from openprocurement.api.constants import AgreementType
from openprocurement.api.procedure.models.base import Model, validate_uniq_code, validate_uniq_id
from openprocurement.api.procedure.models.milestone import Milestone
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTime
from openprocurement.framework.cfaua.constants import CFAUAAgreementType
from openprocurement.framework.cfaua.procedure.models.change import (
    ChangeItemPriceVariation,
    ChangePartyWithdrawal,
    ChangeTaxRate,
    ChangeThirdParty,
    PostChangeItemPriceVariation,
    PostChangePartyWithdrawal,
    PostChangeTaxRate,
    PostChangeThirdParty,
)
from openprocurement.framework.cfaua.procedure.models.contract import Contract
from openprocurement.framework.cfaua.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.framework.cfaua.procedure.models.feature import Feature
from openprocurement.framework.cfaua.procedure.models.item import Item
from openprocurement.framework.cfaua.procedure.models.organization import (
    ProcuringEntity,
)
from openprocurement.framework.core.procedure.models.agreement import (
    CommonAgreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.agreement import (
    CommonPostAgreement as BasePostAgreement,
)
from openprocurement.framework.core.procedure.models.agreement import (
    PatchAgreement as BasePatchAgreement,
)


class Agreement(BaseAgreement):
    agreementNumber: str | None = None
    agreementType: CFAUAAgreementType = AgreementType.CLOSE_FRAMEWORK_AGREEMENT_UA
    period: Period | None = None
    dateSigned: IsoDateTime | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    changes: list[
        Annotated[
            ChangeTaxRate | ChangeItemPriceVariation | ChangePartyWithdrawal | ChangeThirdParty,
            Field(discriminator="rationaleType"),
        ]
    ] = []
    documents: list[Document] = []
    contracts: list[Contract] = []
    features: list[Feature] | None = None
    items: list[Item] | None = None
    procuringEntity: ProcuringEntity
    tender_token: str
    tender_id: str
    milestones: list[Milestone] | None = None

    @computed_field
    def numberOfContracts(self) -> Any:
        return len([c.id for c in self.contracts if c.status == "active"])

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class PostAgreement(BasePostAgreement):
    agreementNumber: str | None = None
    agreementType: CFAUAAgreementType = AgreementType.CLOSE_FRAMEWORK_AGREEMENT_UA
    period: Period | None = None
    dateSigned: IsoDateTime | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    changes: list[
        Annotated[
            PostChangeTaxRate | PostChangeItemPriceVariation | PostChangePartyWithdrawal | PostChangeThirdParty,
            Field(discriminator="rationaleType"),
        ]
    ] = []
    documents: list[PostDocument] = []
    contracts: list[Contract] = []
    features: list[Feature] | None = None
    items: list[Item] | None = None
    procuringEntity: ProcuringEntity
    tender_token: str
    tender_id: str
    milestones: list[Milestone] | None = None

    @field_validator("agreementType", mode="before")
    @classmethod
    def validate_agreement_type(cls, value: Any) -> str:
        # Override value sent by bridge
        # TODO: remove this after bridge is updated
        # TODO: or remove that bridge for the god's sake
        return AgreementType.CLOSE_FRAMEWORK_AGREEMENT_UA

    @computed_field
    def numberOfContracts(self) -> Any:
        return len([c.id for c in self.contracts if c.status == "active"])

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class PatchActiveAgreement(BasePatchAgreement):
    documents: list[PostDocument] | None = None


class PatchTerminatedAgreement(Model):
    pass


class PatchAgreementByAdministrator(BasePatchAgreement):
    documents: list[PostDocument] | None = None
    procuringEntity: ProcuringEntity | None = None
    mode: Literal["test"] | None = None
