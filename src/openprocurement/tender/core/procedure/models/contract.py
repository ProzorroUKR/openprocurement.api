from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import FloatType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_contract, get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.organization import (
    BusinessOrganization,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso


class ContractValue(Value):
    amountNet = FloatType(min_value=0)


# BASE ---
class CommonContract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    buyerID = StringType()
    awardID = StringType(required=True)
    contractID = StringType()
    contractNumber = StringType()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    status = StringType(
        choices=[
            "pending",
            "pending.winner-signing",
            "terminated",
            "active",
            "cancelled",
        ],
        default="pending",
    )
    period = ModelType(Period)
    value = ModelType(ContractValue)
    dateSigned = IsoDateTimeType()
    items = ListType(ModelType(Item, required=True))
    suppliers = ListType(ModelType(BusinessOrganization), min_size=1, max_size=1)
    date = IsoDateTimeType()

    def validate_awardID(self, _, awardID):
        tender = get_tender()
        if awardID and awardID not in [i.get("id") for i in tender.get("awards", [])]:
            raise ValidationError("awardID should be one of awards")

    def validate_dateSigned(self, data, value):
        if not value:
            return
        tender = get_tender()
        skip_award_complaint_period = tender.get("config", {}).get("hasAwardComplaints") is False
        award = [i for i in tender.get("awards", []) if i["id"] == data["awardID"]][0]
        if award.get("complaintPeriod"):
            if not skip_award_complaint_period:
                if award.get("complaintPeriod", {}).get("endDate") and value <= dt_from_iso(
                    award["complaintPeriod"]["endDate"]
                ):
                    raise ValidationError(
                        "Contract signature date should be after award complaint period end date ({})".format(
                            award.get("complaintPeriod", {}).get("endDate", "")
                        )
                    )
            elif award.get("complaintPeriod", {}).get("startDate") and value <= dt_from_iso(
                award["complaintPeriod"]["startDate"]
            ):
                raise ValidationError(
                    "Contract signature date should be after award activation date ({})".format(
                        award.get("complaintPeriod", {}).get("startDate")
                    )
                )
        if value > get_now():
            raise ValidationError("Contract signature date can't be in the future")


# --- BASE


# POST ---
class PostContract(CommonContract):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def status(self):
        return "pending"

    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


# -- POST


# PATCH ---
class PatchContract(Model):
    buyerID = StringType()
    contractNumber = StringType()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    status = StringType(
        choices=[
            "pending",
            "pending.winner-signing",
            "terminated",
            "active",
            "cancelled",
        ]
    )
    period = ModelType(Period)
    value = ModelType(ContractValue)
    dateSigned = IsoDateTimeType()
    items = ListType(ModelType(Item, required=True))

    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


# --- PATCH


# PATCH Supplier---
class PatchContractSupplier(Model):
    status = StringType(
        choices=[
            "pending",
            "pending.winner-signing",
            "terminated",
            "active",
            "cancelled",
        ]
    )


# --- PATCH Supplier


class MetaContract(Model):
    date = IsoDateTimeType()
    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()


# model to validate a contract after patch
class Contract(MetaContract, CommonContract):
    documents = ListType(ModelType(Document, required=True))
    dateSigned = IsoDateTimeType()


def validate_item_unit_values(data, items):
    base_value = data.get("value")
    if base_value is None:
        base_value = (get_contract() or {}).get("value")
    if base_value and items:
        for item in items:
            item_value = (item.get("unit") or {}).get("value")
            if item_value:
                if (
                    get_tender()["config"]["valueCurrencyEquality"] is True
                    and item_value["currency"] != base_value["currency"]
                ):
                    raise ValidationError(f"Value mismatch. Expected: currency {base_value['currency']}")
                if item_value["valueAddedTaxIncluded"] != base_value["valueAddedTaxIncluded"]:
                    raise ValidationError(
                        f"Value mismatch. Expected: valueAddedTaxIncluded {base_value['valueAddedTaxIncluded']}"
                    )
