from decimal import Decimal
from uuid import uuid4
from schematics.types import StringType
from schematics.types.compound import PolyModelType
from schematics.types.serializable import serializable
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, ModelType, DecimalType, IsoDateTimeType
from openprocurement.api.procedure.models.item import (
    AdditionalClassification,
    Item as BaseItem,
)
from openprocurement.api.procedure.models.organization import Organization, PROCURING_ENTITY_KINDS
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.utils import get_change_class
from openprocurement.framework.cfaua.procedure.models.change import (
    ChangeTaxRate,
    ChangePartyWithdrawal,
    ChangeThirdParty,
    ChangeItemPriceVariation,
    PostChangeTaxRate,
    PostChangeItemPriceVariation,
    PostChangePartyWithdrawal,
    PostChangeThirdParty,
)
from openprocurement.framework.cfaua.procedure.models.contract import Contract
from openprocurement.framework.cfaua.procedure.models.document import Document
from openprocurement.framework.core.procedure.models.contact import ContactPoint as BaseContactPoint
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
    PatchAgreement as BasePatchAgreement,
    PostAgreement as BasePostAgreement,
)
from openprocurement.api.procedure.validation import validate_values_uniq, validate_features_uniq
from openprocurement.framework.core.procedure.models.item import CPVClassification


class FeatureValue(Model):
    value = DecimalType(required=True, min_value=Decimal("0.0"), max_value=Decimal("0.3"))
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()


class Feature(Model):
    code = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    featureOf = StringType(required=True, choices=["tenderer", "lot", "item"], default="tenderer")
    relatedItem = StringType(min_length=1)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    enum = ListType(
        ModelType(FeatureValue, required=True), default=list(), min_size=1, validators=[validate_values_uniq]
    )


class Item(BaseItem):
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, default=list()))
    description_en = StringType(required=True, min_length=1)
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)
    unit = ModelType(Unit)


class ContactPoint(BaseContactPoint):
    availableLanguage = StringType(required=True, choices=["uk", "en", "ru"], default="uk")

    def validate_telephone(self, data, value):
        pass


class ProcuringEntity(Organization):
    """An organization."""

    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address, required=True)


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
            (ChangeTaxRate, ChangeItemPriceVariation, ChangePartyWithdrawal, ChangeThirdParty),
            claim_function=get_change_class,
        ),
        default=list(),
    )
    documents = ListType(ModelType(Document, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    procuringEntity = ModelType(ProcuringEntity, required=True)
    terminationDetails = StringType()
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
            (PostChangeTaxRate, PostChangeItemPriceVariation, PostChangePartyWithdrawal, PostChangeThirdParty),
            claim_function=get_change_class,
        ),
        default=list(),
    )
    documents = ListType(ModelType(Document, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    procuringEntity = ModelType(ProcuringEntity, required=True)
    terminationDetails = StringType()
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)

    @serializable
    def numberOfContracts(self):
        return len([c.id for c in self.contracts if c.status == "active"])


class PatchActiveAgreement(BasePatchAgreement):
    documents = ListType(ModelType(Document), default=list())
    terminationDetails = StringType()


class PatchTerminatedAgreement(Model):
    pass


class PatchAgreementByAdministrator(Model):
    documents = ListType(ModelType(Document), default=list())
    procuringEntity = ModelType(ProcuringEntity)
    terminationDetails = StringType()
    status = StringType(choices=["active", "terminated"])
    mode = StringType(choices=["test"])
