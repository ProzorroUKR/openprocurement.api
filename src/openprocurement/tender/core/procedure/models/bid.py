from uuid import uuid4

from schematics.types import BooleanType, MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.core.procedure.models.base import BaseBid
from openprocurement.tender.core.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.tender.core.procedure.models.item import LocalizationItem
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue,
    PatchLotValue,
    PostLotValue,
)
from openprocurement.tender.core.procedure.models.organization import Supplier
from openprocurement.tender.core.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)
from openprocurement.tender.core.procedure.models.req_response import (
    ObjResponseMixin,
)
from openprocurement.tender.core.procedure.models.value import (
    WeightedValue,
)


# PATCH DATA ---
class PatchBid(ObjResponseMixin, BaseBid):
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


class AdministratorPatchBid(Model):
    """
    Administrator may only fix the supplier identity of a bid,
    the commercial part (value, lotValues, status, ...) is untouchable
    """

    tenderers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)


class PatchQualificationBid(PatchBid):
    lotValues = ListType(ModelType(LotValue, required=True))


# --- PATCH DATA


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


# --- BASE


# POST DATA ---
class PostBid(ObjResponseMixin, CommonBid):
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
class Bid(MetaBid, ObjResponseMixin, CommonBid):
    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))
    selfQualified = BooleanType(choices=[True])
    selfEligible = BooleanType(choices=[True])
