from schematics.types import StringType
from schematics.types.compound import PolyModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.procedure.validation import validate_features_uniq
from openprocurement.api.utils import get_change_class
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
    agreementNumber = StringType()
    agreementType = StringType(default="cfaua")
    period = ModelType(Period)
    dateSigned = IsoDateTimeType()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    changes = ListType(
        PolyModelType(
            (
                ChangeTaxRate,
                ChangeItemPriceVariation,
                ChangePartyWithdrawal,
                ChangeThirdParty,
            ),
            claim_function=get_change_class,
        ),
        default=[],
    )
    documents = ListType(ModelType(Document, required=True), default=[])
    contracts = ListType(ModelType(Contract, required=True), default=[])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    procuringEntity = ModelType(ProcuringEntity, required=True)
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)

    @serializable
    def numberOfContracts(self):
        return len([c.id for c in self.contracts if c.status == "active"])


class PostAgreement(BasePostAgreement):
    agreementNumber = StringType()
    agreementType = StringType(default="cfaua")
    period = ModelType(Period)
    dateSigned = IsoDateTimeType()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    changes = ListType(
        PolyModelType(
            (
                PostChangeTaxRate,
                PostChangeItemPriceVariation,
                PostChangePartyWithdrawal,
                PostChangeThirdParty,
            ),
            claim_function=get_change_class,
        ),
        default=[],
    )
    documents = ListType(ModelType(PostDocument, required=True), default=[])
    contracts = ListType(ModelType(Contract, required=True), default=[])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    procuringEntity = ModelType(ProcuringEntity, required=True)
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)

    @serializable
    def numberOfContracts(self):
        return len([c.id for c in self.contracts if c.status == "active"])


class PatchActiveAgreement(BasePatchAgreement):
    documents = ListType(ModelType(PostDocument))


class PatchTerminatedAgreement(Model):
    pass


class PatchAgreementByAdministrator(BasePatchAgreement):
    documents = ListType(ModelType(PostDocument))
    procuringEntity = ModelType(ProcuringEntity)
    mode = StringType(choices=["test"])
