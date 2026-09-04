from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types import BooleanType, MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.core.constants import BID_LOTVALUES_VALIDATION_FROM
from openprocurement.tender.core.procedure.models.base import BaseBid
from openprocurement.tender.core.procedure.models.document import (
    CDBidDocument,
    CDBidPostDocument,
    Document,
    PostDocument,
)
from openprocurement.tender.core.procedure.models.item import LocalizationItem
from openprocurement.tender.core.procedure.models.lot_value import (
    ARMALotValue,
    ARMAPatchLotValue,
    ARMAPostLotValue,
    CDLotValue,
    CDPatchLotValue,
    CDPostLotValue,
    ESCOLotValue,
    ESCOPatchLotValue,
    ESCOPostLotValue,
    LotValue,
    PatchLotValue,
    PostLotValue,
)
from openprocurement.tender.core.procedure.models.organization import Supplier
from openprocurement.tender.core.procedure.models.parameter import (
    CFASelectionParameter,
    CFASelectionPatchParameter,
    Parameter,
    PatchParameter,
)
from openprocurement.tender.core.procedure.models.req_response import (
    BidResponsesMixin,
    PatchObjResponsesMixin,
)
from openprocurement.tender.core.procedure.models.value import (
    AmountPercentageWeightedValue,
    ESCODynamicValue,
    ESCOPatchValue,
    ESCOWeightedValue,
    WeightedValue,
)
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import validate_bid_value


# PATCH DATA ---
class PatchBid(PatchObjResponsesMixin, BaseBid):
    items = ListType(ModelType(LocalizationItem, required=True))
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_uniq_code])
    value = ModelType(Value)
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    tenderers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    status = StringType(
        choices=[
            "draft",
            "pending",
            "active",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ],
    )
    subcontractingDetails = StringType()
    # choices=[True]; whether the fields are required/rogue is validated in BidState
    selfQualified = BooleanType(choices=[True])
    selfEligible = BooleanType(choices=[True])


class PatchQualificationBid(PatchBid):
    lotValues = ListType(ModelType(LotValue, required=True))


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
    items = ListType(ModelType(LocalizationItem, required=True), min_size=1, validators=[validate_uniq_id])
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])
    value = ModelType(Value)
    initialValue = ModelType(Value)  # field added by chronograph
    participationUrl = StringType()  # field added after auction
    lotValues = ListType(ModelType(LotValue, required=True))
    tenderers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    status = StringType(
        choices=[
            "draft",
            "pending",
            "active",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ],
        required=True,
    )
    subcontractingDetails = StringType()
    weightedValue = ModelType(WeightedValue)

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
                or i["featureOf"] == "lot"
                and i["relatedItem"] in lots
                or i["featureOf"] == "item"
                and i["relatedItem"] in items
            }
            if {i["code"] for i in parameters} != set(codes):
                raise ValidationError("All features parameters is required.")
        elif not parameters and tender.get("features"):
            raise ValidationError("This field is required.")
        elif {i["code"] for i in parameters} != {i["code"] for i in tender.get("features", "")}:
            raise ValidationError("All features parameters is required.")


# --- BASE


# POST DATA ---
class PostBid(BidResponsesMixin, CommonBid):
    @serializable
    def id(self):
        return uuid4().hex

    tenderers = ListType(
        ModelType(Supplier, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    lotValues = ListType(ModelType(PostLotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])
    status = StringType(
        choices=[
            "draft",
            "pending",
            "active",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ],
        default="draft",
    )
    documents = ListType(ModelType(PostDocument, required=True))
    financialDocuments = ListType(ModelType(PostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True))
    qualificationDocuments = ListType(ModelType(PostDocument, required=True))
    # choices=[True]; whether the fields are required/rogue is validated in BidState
    selfQualified = BooleanType(choices=[True])
    selfEligible = BooleanType(choices=[True])


# -- POST


class MetaBid(Model):
    id = MD5Type()
    date = StringType()
    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()
    submissionDate = IsoDateTimeType()


# model to validate a bid after patch
class Bid(MetaBid, BidResponsesMixin, CommonBid):
    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))
    selfQualified = BooleanType(choices=[True])
    selfEligible = BooleanType(choices=[True])

    def validate_value(self, data, value):
        pass  # validated in BidState.validate_bid_value_on_patch (draft bids differ per procedure)


Administrator_bid_role = whitelist("tenderers")


def filter_administrator_bid_update(request, data):
    if request.authenticated_role == "Administrator":
        data = {k: v for k, v in data.items() if not Administrator_bid_role(k, v)}
    return data


# --- ESCO ---


class ESCOBidMixin(Model):
    value = ModelType(ESCODynamicValue)
    weightedValue = ModelType(ESCOWeightedValue)
    lotValues = ListType(ModelType(ESCOLotValue, required=True))
    selfQualified = BooleanType(required=False)
    selfEligible = BooleanType(required=False)

    def validate_value(self, data, value):
        tender = get_tender()
        if tender.get("lots"):
            if value:
                raise ValidationError("value should be posted for each lot of bid")
        else:
            if not value:
                raise ValidationError("This field is required.")
            if tender["minValue"].get("currency") != value.get("currency"):
                raise ValidationError("currency of bid should be identical to currency of minValue of tender")
            if tender["minValue"].get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
                raise ValidationError(
                    "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of tender"
                )


class ESCOPatchBid(ESCOBidMixin, PatchBid):
    value = ModelType(ESCOPatchValue)
    lotValues = ListType(ModelType(ESCOPatchLotValue, required=True))

    def validate_value(self, data, value):
        return  # will be validated at Bid model


class ESCOPatchQualificationBid(ESCOPatchBid):
    lotValues = ListType(ModelType(ESCOLotValue, required=True))


class ESCOPostBid(ESCOBidMixin, PostBid):
    lotValues = ListType(ModelType(ESCOPostLotValue, required=True))


class ESCOBid(ESCOBidMixin, Bid):
    pass


# --- ARMA (percentage values) ---


class ARMAPatchBid(PatchBid):
    lotValues = ListType(ModelType(ARMAPatchLotValue, required=True))


class ARMAPatchQualificationBid(ARMAPatchBid):
    lotValues = ListType(ModelType(ARMALotValue, required=True))


class ARMAPostBid(PostBid):
    lotValues = ListType(ModelType(ARMAPostLotValue, required=True))


class ARMABid(Bid):
    lotValues = ListType(ModelType(ARMALotValue, required=True))
    weightedValue = ModelType(AmountPercentageWeightedValue)


# --- CFA selection: decimal parameters ---


class CFASelectionPatchBid(PatchBid):
    parameters = ListType(ModelType(CFASelectionPatchParameter, required=True), validators=[validate_uniq_code])


class CFASelectionPatchQualificationBid(PatchQualificationBid):
    parameters = ListType(ModelType(CFASelectionPatchParameter, required=True), validators=[validate_uniq_code])


class CFASelectionPostBid(PostBid):
    parameters = ListType(ModelType(CFASelectionParameter, required=True), validators=[validate_uniq_code])


class CFASelectionBid(Bid):
    parameters = ListType(ModelType(CFASelectionParameter, required=True), validators=[validate_uniq_code])


# --- competitiveDialogue (stage 1): bids without value, lot values without value, decision documents ---


class CDPatchBid(PatchBid):
    lotValues = ListType(ModelType(CDPatchLotValue, required=True))


class CDPatchQualificationBid(CDPatchBid):
    lotValues = ListType(ModelType(CDLotValue, required=True))


class CDPostBid(PostBid):
    lotValues = ListType(ModelType(CDPostLotValue, required=True))
    documents = ListType(ModelType(CDBidPostDocument, required=True))
    financialDocuments = ListType(ModelType(CDBidPostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(CDBidPostDocument, required=True))
    qualificationDocuments = ListType(ModelType(CDBidPostDocument, required=True))

    def validate_value(self, data, value):
        pass  # stage 1 bids have no value

    def validate_parameters(self, data, parameters):
        pass  # stage 1 bids have no parameters


class CDBid(Bid):
    lotValues = ListType(ModelType(CDLotValue, required=True))

    def validate_parameters(self, data, parameters):
        pass  # stage 1 bids have no parameters

    documents = ListType(ModelType(CDBidDocument, required=True))
    financialDocuments = ListType(ModelType(CDBidDocument, required=True))
    eligibilityDocuments = ListType(ModelType(CDBidDocument, required=True))
    qualificationDocuments = ListType(ModelType(CDBidDocument, required=True))
