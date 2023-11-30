from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types import MD5Type, StringType, BaseType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.models import Value, Model
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.constants import BID_LOTVALUES_VALIDATION_FROM
from openprocurement.tender.core.procedure.validation import validate_bid_value, validate_parameters_uniq
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.models.base import ListType, BaseBid
from openprocurement.tender.core.procedure.models.organization import (
    PatchBusinessOrganization,
    PostBusinessOrganization,
)
from openprocurement.tender.core.procedure.models.parameter import Parameter, PatchParameter
from openprocurement.tender.core.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue
from openprocurement.tender.core.procedure.models.bid_document import PostDocument, Document
from openprocurement.tender.core.procedure.models.item import BaseItem


# PATCH DATA ---
class PatchBid(BaseBid):
    items = ListType(ModelType(BaseItem, required=True))
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])
    value = ModelType(Value)
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    tenderers = ListType(ModelType(PatchBusinessOrganization, required=True), min_size=1, max_size=1)
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
    )
# --- PATCH DATA


def validate_lot_values(lot_values):
    tender = get_tender()
    if tender.get("lots") and not lot_values:
        raise ValidationError("This field is required.")
    if tender_created_after(BID_LOTVALUES_VALIDATION_FROM) and lot_values:
        lots = [i["relatedLot"] for i in lot_values]
        if len(lots) != len(set(lots)):
            raise ValidationError("bids don't allow duplicated proposals")


# BASE ---
class CommonBid(BaseBid):
    items = ListType(ModelType(BaseItem, required=True), min_size=1, validators=[validate_items_uniq])
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    value = ModelType(Value)
    lotValues = ListType(ModelType(LotValue, required=True))
    tenderers = ListType(ModelType(PostBusinessOrganization, required=True), min_size=1, max_size=1)
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        required=True,
    )

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)

    def validate_lotValues(self, data, values):
        validate_lot_values(values)

    def validate_parameters(self, data, parameters):
        lot_values = data.get("lotValues") or ""
        tender = get_tender()
        parameters = parameters or []

        if tender.get("lots"):
            lots = [i["relatedLot"] for i in lot_values]
            items = [i["id"] for i in tender.get("items", "") if i.get("relatedLot") in lots]
            codes = {
                i["code"]: [x["value"] for x in i["enum"]]
                for i in tender.get("features", "")
                if i["featureOf"] == "tenderer"
                   or i["featureOf"] == "lot" and i["relatedItem"] in lots
                   or i["featureOf"] == "item" and i["relatedItem"] in items
            }
            if set(i["code"] for i in parameters) != set(codes):
                raise ValidationError("All features parameters is required.")
        elif not parameters and tender.get("features"):
            raise ValidationError("This field is required.")
        elif set(i["code"] for i in parameters) != set(i["code"] for i in tender.get("features", "")):
            raise ValidationError("All features parameters is required.")
# --- BASE


# POST DATA ---
class PostBid(CommonBid):
    @serializable
    def id(self):
        return uuid4().hex

    items = ListType(ModelType(BaseItem, required=True), min_size=1, validators=[validate_items_uniq])
    tenderers = ListType(ModelType(PostBusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    lotValues = ListType(ModelType(PostLotValue, required=True))
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        default="draft",
    )
    documents = ListType(ModelType(PostDocument, required=True))
    financialDocuments = ListType(ModelType(PostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True))
    qualificationDocuments = ListType(ModelType(PostDocument, required=True))

# -- POST


class MetaBid(Model):
    id = MD5Type()
    date = StringType()
    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()


# model to validate a bid after patch
class Bid(MetaBid, CommonBid):
    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))


Administrator_bid_role = whitelist("tenderers")


def filter_administrator_bid_update(request, data):
    if request.authenticated_role == "Administrator":
        data = {k: v for k, v in data.items() if not Administrator_bid_role(k, v)}
    return data
