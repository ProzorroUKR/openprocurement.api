# -*- coding: utf-8 -*-
from uuid import uuid4
from zope.interface import implementer, Interface

# from couchdb_schematics.document import SchematicsDocument
from pyramid.security import Allow
from schematics.types import StringType, BaseType, MD5Type, FloatType
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.api.utils import get_now
from openprocurement.api.models import Contract as BaseContract
from openprocurement.api.models import OpenprocurementSchematicsDocument as SchematicsDocument
from openprocurement.api.models import Document as BaseDocument
from openprocurement.api.models import Organization as BaseOrganization
from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.models import CPVClassification as BaseCPVClassification
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import AdditionalClassification as BaseAdditionalClassification
from openprocurement.api.models import Model, ListType, Revision, Value, IsoDateTimeType, Guarantee
from openprocurement.api.validation import validate_items_uniq
from openprocurement.api.models import plain_role, schematics_default_role, schematics_embedded_role
from openprocurement.api.interfaces import IOPContent
from openprocurement.tender.core.models import Tender, ContractValue, PROCURING_ENTITY_KINDS
from openprocurement.api.models import BankAccount

contract_create_role = whitelist(
    "id",
    "awardID",
    "contractID",
    "contractNumber",
    "title",
    "title_en",
    "title_ru",
    "description",
    "description_en",
    "description_ru",
    "status",
    "period",
    "value",
    "dateSigned",
    "items",
    "suppliers",
    "procuringEntity",
    "owner",
    "tender_token",
    "tender_id",
    "mode",
)

contract_edit_role = whitelist(
    "title",
    "title_en",
    "title_ru",
    "description",
    "description_en",
    "description_ru",
    "status",
    "period",
    "value",
    "items",
    "amountPaid",
    "terminationDetails",
    "contract_amountPaid",
    "implementation"
)

contract_view_role = whitelist(
    "id",
    "awardID",
    "contractID",
    "dateModified",
    "contractNumber",
    "title",
    "title_en",
    "title_ru",
    "description",
    "description_en",
    "description_ru",
    "status",
    "period",
    "value",
    "dateSigned",
    "documents",
    "items",
    "suppliers",
    "procuringEntity",
    "owner",
    "mode",
    "tender_id",
    "changes",
    "amountPaid",
    "terminationDetails",
    "contract_amountPaid",
    "implementation",
)

contract_administrator_role = Tender.Options.roles["Administrator"] + whitelist("suppliers")

item_edit_role = whitelist(
    "description",
    "description_en",
    "description_ru",
    "unit",
    "deliveryDate",
    "deliveryAddress",
    "deliveryLocation",
    "quantity",
    "id",
)


class IContract(IOPContent):
    """ Contract marker interface """


def get_contract(model):
    while not IContract.providedBy(model):
        model = model.__parent__
    return model


class Document(BaseDocument):
    """ Contract Document """

    documentOf = StringType(required=True, choices=["tender", "item", "lot", "contract", "change"], default="contract")

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("documentOf") in ["item", "change"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            contract = get_contract(parent)
            if data.get("documentOf") == "change" and relatedItem not in [i.id for i in contract.changes]:
                raise ValidationError(u"relatedItem should be one of changes")
            if data.get("documentOf") == "item" and relatedItem not in [i.id for i in contract.items]:
                raise ValidationError(u"relatedItem should be one of items")


class TransactionDocument(BaseDocument):
    """ Contract Transaction Document """

    documentOf = StringType(required=True, default="contract")


class ContactPoint(BaseContactPoint):
    availableLanguage = StringType()


class Organization(BaseOrganization):
    """An organization."""

    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)


class BusinessOrganization(Organization):
    """An organization."""

    scale = StringType(choices=SCALE_CODES)


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        roles = {
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "edit_active": schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        pass


class AdditionalClassification(BaseAdditionalClassification):
    def validate_id(self, data, code):
        pass


class Item(BaseItem):
    class Options:
        roles = {"edit_active": item_edit_role, "view": schematics_default_role, "embedded": schematics_embedded_role}

    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True), default=list())


class Change(Model):
    class Options:
        roles = {
            # 'edit': blacklist('id', 'date'),
            "create": whitelist(
                "rationale", "rationale_ru", "rationale_en", "rationaleTypes", "contractNumber", "dateSigned"
            ),
            "edit": whitelist(
                "rationale", "rationale_ru", "rationale_en", "rationaleTypes", "contractNumber", "status", "dateSigned"
            ),
            "view": schematics_default_role,
            "embedded": schematics_embedded_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["pending", "active"], default="pending")
    date = IsoDateTimeType(default=get_now)
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    rationaleTypes = ListType(
        StringType(
            choices=[
                "volumeCuts",
                "itemPriceVariation",
                "qualityImprovement",
                "thirdParty",
                "durationExtension",
                "priceReduction",
                "taxRate",
                "fiscalYearExtension",
            ],
            required=True,
        ),
        min_size=1,
        required=True,
    )
    contractNumber = StringType()
    dateSigned = IsoDateTimeType()

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError(u"Contract signature date can't be in the future")


class OrganizationReference(Model):
    bankAccount = ModelType(BankAccount, required=True)
    name = StringType(required=True)


class Transaction(Model):
    id = StringType(required=True)
    documents = ListType(ModelType(TransactionDocument), default=list())
    date = IsoDateTimeType(required=True)
    value = ModelType(Guarantee, required=True)
    payer = ModelType(OrganizationReference, required=True)
    payee = ModelType(OrganizationReference, required=True)
    status = StringType(required=True)

    class Options:
        roles = {
            "view": schematics_default_role,
        }


class Implementation(Model):
    transactions = ListType(ModelType(Transaction), default=list())


@implementer(IContract)
class Contract(SchematicsDocument, BaseContract):
    """ Contract """

    revisions = ListType(ModelType(Revision, required=True), default=list())
    dateModified = IsoDateTimeType()
    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    items = ListType(ModelType(Item, required=True), required=False, min_size=1, validators=[validate_items_uniq])
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)
    owner_token = StringType(default=lambda: uuid4().hex)
    transfer_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=["test"])
    status = StringType(choices=["terminated", "active"], default="active")
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    changes = ListType(ModelType(Change, required=True), default=list())
    documents = ListType(ModelType(Document, required=True), default=list())
    amountPaid = ModelType(ContractValue)
    value = ModelType(ContractValue)
    terminationDetails = StringType()
    implementation = ModelType(Implementation, default=dict())

    create_accreditations = (ACCR_3, ACCR_5)  # TODO

    class Options:
        roles = {
            "plain": plain_role,
            "create": contract_create_role,
            "edit_active": contract_edit_role,
            "edit_terminated": whitelist(),
            "view": contract_view_role,
            "Administrator": contract_administrator_role,
            "default": schematics_default_role,
        }

    def __local_roles__(self):
        return dict(
            [
                ("{}_{}".format(self.owner, self.owner_token), "contract_owner"),
                ("{}_{}".format(self.owner, self.tender_token), "tender_owner"),
            ]
        )

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_contract"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_contract_documents"),
            (Allow, "{}_{}".format(self.owner, self.tender_token), "generate_credentials"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_contract_transactions"),
            (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_contract_transaction_documents"),
        ]
        return acl

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        else:
            role = "edit_{}".format(request.context.status)
        return role

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    @serializable(serialized_name="amountPaid", serialize_when_none=False, type=ModelType(Value))
    def contract_amountPaid(self):
        if self.amountPaid:
            value = self.value or self.amountPaid
            return ContractValue(
                dict(
                    amount=self.amountPaid.amount,
                    amountNet=self.amountPaid.amountNet,
                    currency=value.currency,
                    valueAddedTaxIncluded=value.valueAddedTaxIncluded,
                )
            )
