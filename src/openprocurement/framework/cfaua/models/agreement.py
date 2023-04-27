from decimal import Decimal
from uuid import uuid4

from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType, ListType, PolyModelType
from schematics.types.serializable import serializable

from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.api.models import BusinessOrganization as BaseBusinessOrganization
from openprocurement.api.models import (
    ContactPoint as BaseContactPoint,
    Organization,
    DecimalType,
    Model,
    IsoDateTimeType,
    Period,
)
from openprocurement.api.models import Document as BaseDocument
from openprocurement.api.models import (
    Item as BaseItem,
    ListType as BaseListType,
    Unit,
    CPVClassification,
    AdditionalClassification,
    PeriodEndRequired,
    BaseAddress,
)
from openprocurement.api.models import Value as BaseValue
from openprocurement.api.utils import get_now, get_change_class
from openprocurement.framework.cfaua.validation import (
    validate_values_uniq,
    validate_modifications_items_uniq,
    validate_only_addend_or_only_factor,
    validate_item_price_variation_modifications,
    validate_third_party_modifications,
    validate_modifications_contracts_uniq,
    validate_parameters_uniq,
    validate_features_uniq,
)
from openprocurement.framework.core.models import (
    Agreement as BaseAgreement,
    get_agreement,
)

PROCURING_ENTITY_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")


class Value(BaseValue):
    amount = DecimalType(required=True, precision=-2, min_value=Decimal("0.0"))


class UnitPrice(Model):
    class Options:
        roles = Model.Options.roles

    # TODO: validate relatedItem? (quintagroup)
    relatedItem = StringType()
    value = ModelType(Value)


class ContactPoint(BaseContactPoint):
    class Options:
        roles = BaseContactPoint.Options.roles

    availableLanguage = StringType(required=True, choices=["uk", "en", "ru"], default="uk")

    def validate_telephone(self, data, value):
        pass


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

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("featureOf") in ["item", "lot"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if isinstance(parent, Model):
            if data.get("featureOf") == "item" and relatedItem not in [i.id for i in parent.items]:
                raise ValidationError(u"relatedItem should be one of items")
            if data.get("featureOf") == "lot" and relatedItem not in [i.id for i in parent.lots]:
                raise ValidationError(u"relatedItem should be one of lots")


class UnitDeprecated(Unit):
    def validate_code(self, data, value):
        pass


class Item(BaseItem):
    class Options:
        roles = BaseItem.Options.roles

    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = BaseListType(ModelType(AdditionalClassification, default=list()))
    description_en = StringType(required=True, min_length=1)
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(BaseAddress, required=True)
    unit = ModelType(UnitDeprecated)


class UnitPriceModification(Model):
    class Options:
        roles = {
            "edit": blacklist("id", "__parent__"),
            "default": blacklist("__parent__"),
            "create": blacklist("id", "__parent__"),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    itemId = StringType()
    factor = DecimalType(required=False, precision=-4, min_value=Decimal("0.0"))
    addend = DecimalType(required=False, precision=-2)


class ContractModification(Model):
    class Options:
        roles = {
            "edit": blacklist("id", "__parent__"),
            "default": blacklist("__parent__"),
            "create": blacklist("id", "__parent__"),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    itemId = StringType()
    contractId = StringType(required=True)


class Parameter(Model):
    class Options:
        serialize_when_none = False
        roles = Model.Options.roles

    code = StringType(required=True)
    value = DecimalType(required=True)

    def validate_code(self, data, code):
        if isinstance(data["__parent__"], Model) and code not in [
            i.code for i in (get_agreement(data["__parent__"]).features or [])
        ]:
            raise ValidationError(u"code should be one of feature code.")

    def validate_value(self, data, value):
        if isinstance(data["__parent__"], Model):
            agreement = get_agreement(data["__parent__"])
            codes = dict([(i.code, [x.value for x in i.enum]) for i in (agreement.features or [])])
            if data["code"] in codes and value not in codes[data["code"]]:
                raise ValidationError(u"value should be one of feature value.")


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        # TODO: do we really need roles here (quintagroup)
        roles = {
            "default": blacklist("__parent__"),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = BaseListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(BaseAddress, required=True)


class Change(Model):
    class Options:
        roles = {
            "edit": blacklist("date", "id", "__parent__"),
            "default": blacklist("__parent__"),
            "create": blacklist("status", "date", "id", "__parent__"),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["pending", "active", "cancelled"], default="pending")
    date = IsoDateTimeType(default=get_now)
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    dateSigned = IsoDateTimeType()
    agreementNumber = StringType()

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError(u"Agreement signature date can't be in the future")


class ChangeTaxRate(Change):
    class Options:
        namespace = "Change"
        roles = {
            "edit": blacklist("date", "id", "__parent__", "rationaleType"),
            "default": blacklist("__parent__"),
            "create": blacklist("status", "date", "id", "__parent__"),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__")
        }

    rationaleType = StringType(default="taxRate")
    modifications = BaseListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_modifications_items_uniq, validate_only_addend_or_only_factor],
    )


class ChangeItemPriceVariation(Change):
    class Options:
        namespace = "Change"
        roles = {
            "edit": blacklist("date", "id", "__parent__", "rationaleType"),
            "default": blacklist("__parent__"),
            "create": blacklist("status", "id", "__parent__"),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    rationaleType = StringType(default="itemPriceVariation")
    modifications = BaseListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_item_price_variation_modifications, validate_modifications_items_uniq],
    )


class ChangeThirdParty(Change):
    class Options:
        namespace = "Change"
        roles = {
            "edit": blacklist("date", "id", "__parent__", "rationaleType"),
            "default": blacklist("__parent__"),
            "create": blacklist("status", "date", "id", "__parent__", ),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    rationaleType = StringType(default="thirdParty")
    modifications = BaseListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_third_party_modifications, validate_modifications_items_uniq],
    )


class ChangePartyWithdrawal(Change):
    class Options:
        namespace = "Change"
        roles = {
            "edit": blacklist("date", "id", "__parent__", "rationaleType"),
            "default": blacklist("__parent__"),
            "create": blacklist("status", "date", "id", "__parent__"),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    rationaleType = StringType(default="partyWithdrawal")
    modifications = BaseListType(
        ModelType(ContractModification, required=True), validators=[validate_modifications_contracts_uniq]
    )


class BusinessOrganization(BaseBusinessOrganization):
    address = ModelType(BaseAddress, required=True)

    def validate_scale(self, data, value):
        pass


class Contract(Model):
    class Options:
        roles = {
            "edit": blacklist("status", "unitPrices", "suppliers", "bidID", "date", "awardID", "id", "__parent__",
                              "parameters"),
            "default": blacklist("__parent__"),
            "create": blacklist(),
            "embedded": blacklist("__parent__"),
            "view": blacklist("__parent__"),
        }

    id = MD5Type(required=True)

    # TODO: validate me (quintagroup)
    status = StringType(choices=["active", "unsuccessful"])
    suppliers = BaseListType(ModelType(BusinessOrganization, required=True))
    unitPrices = BaseListType(ModelType(UnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
    parameters = BaseListType(ModelType(Parameter, required=True), default=list(),
                              validators=[validate_parameters_uniq])


class Document(BaseDocument):
    class Options:
        roles = {
            "embedded": blacklist("download_url", "url", "__parent__"),
            "default": blacklist("__parent__"),
            "create": blacklist("download_url", "datePublished", "author", "dateModified", "id"),
            "edit": blacklist("download_url", "hash", "url", "datePublished", "author", "dateModified", "id"),
            "revisions": whitelist("url", "dateModified"),
            "view": blacklist("__parent__"),
        }

    documentOf = StringType(
        required=True, choices=["tender", "item", "contract", "agreement", "lot", "change"], default="agreement"
    )


class Agreement(BaseAgreement):
    class Options:
        _data_fields = whitelist(
            "agreementID", "agreementNumber", "changes", "contracts", "dateSigned", "description",
            "description_en", "description_ru", "documents", "features", "doc_id", "items", "mode",
            "numberOfContracts", "owner", "period", "procuringEntity", "status", "tender_id",
            "terminationDetails", "title", "title_en", "title_ru"
        )
        _create = _data_fields + whitelist("tender_token")
        _embedded = _create + whitelist(
            "dateModified", "agreementType", "revisions",
            "owner_token", "date", "transfer_token", "doc_id",
        )
        roles = {
            "view": _data_fields + whitelist("dateModified"),
            "create": _create,
            "edit_terminated": whitelist(),
            "edit_active": whitelist("documents", "status", "terminationDetails"),
            "Administrator": whitelist("documents", "mode", "procuringEntity", "status", "terminationDetails"),
            "embedded": _embedded,
            "default": _embedded - whitelist("doc_id") + whitelist("_id", "_rev", "doc_type"),
            "plain": _embedded - whitelist("revisions", "dateModified"),
        }

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
    changes = BaseListType(
        PolyModelType(
            (ChangeTaxRate, ChangeItemPriceVariation, ChangePartyWithdrawal, ChangeThirdParty),
            claim_function=get_change_class,
        ),
        default=list(),
    )
    documents = BaseListType(ModelType(Document, required=True), default=list())
    contracts = BaseListType(ModelType(Contract, required=True), default=list())
    features = BaseListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = BaseListType(ModelType(Item, required=True))
    procuringEntity = ModelType(ProcuringEntity, required=True)
    terminationDetails = StringType()
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)

    create_accreditations = (ACCR_3, ACCR_5)

    def __local_roles__(self):
        return dict(
            [
                ("{}_{}".format(self.owner, self.owner_token), "agreement_owner"),
                ("{}_{}".format(self.owner, self.tender_token), "tender_owner"),
            ]
        )

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_agreement"),
            (Allow, "{}_{}".format(self.owner, self.tender_token), "generate_credentials"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_agreement_documents")
        ]
        return acl

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        else:
            role = "edit_{}".format(request.context.status)
        return role

    def get_active_contracts_count(self):
        return len([c.id for c in self.contracts if c.status == "active"])

    @serializable
    def numberOfContracts(self):
        return len([c.id for c in self.contracts if c.status == "active"])
