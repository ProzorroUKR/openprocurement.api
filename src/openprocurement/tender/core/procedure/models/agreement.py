from decimal import Decimal
from uuid import uuid4

from isodate import duration_isoformat
from schematics.exceptions import ValidationError
from schematics.types import BaseType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType, PolyModelType

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import DecimalType, IsoDateTimeType, ListType
from openprocurement.api.utils import get_change_class
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.cfaua.constants import MAX_AGREEMENT_PERIOD
from openprocurement.tender.core.procedure.models.agreement_contract import (
    CFAAgreementContract,
    CFASelectionAgreementContract,
)
from openprocurement.tender.core.procedure.models.feature import (
    CFAFeature,
    CFASelectionFeature,
    validate_related_items,
)
from openprocurement.tender.core.procedure.models.item import TechFeatureItem
from openprocurement.tender.core.procedure.models.milestone import Milestone
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.parameter import (
    validate_cfa_selection_parameter_contracts,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso


class AgreementUUID(Model):
    id = MD5Type(required=True)


# --- CFA (closeFrameworkAgreementUA): agreement created by the tender ---


class CFAPatchAgreement(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    status = StringType(choices=["pending", "active", "cancelled", "unsuccessful"])
    period = ModelType(Period)
    dateSigned = IsoDateTimeType()
    agreementNumber = StringType()


class CFAAgreement(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])
    items = ListType(ModelType(TechFeatureItem, required=True))
    period = ModelType(Period)
    status = StringType(choices=["pending", "active", "cancelled", "unsuccessful"], required=True)
    contracts = ListType(ModelType(CFAAgreementContract, required=True))
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    documents = BaseType()

    def validate_features(self, data, features):
        validate_related_items(data, features)

    def validate_dateSigned(self, data, value):
        if value:
            award_ids = [c["awardID"] for c in data["contracts"]]
            award = next(i for i in get_tender().get("awards", []) if i["id"] in award_ids)
            complaint_period = award.get("complaintPeriod")
            if (
                complaint_period
                and complaint_period.get("endDate")
                and value <= dt_from_iso(complaint_period["endDate"])
            ):
                raise ValidationError(
                    "Agreement signature date should be after "
                    f"award complaint period end date ({complaint_period['endDate']})"
                )
            if value > get_request_now():
                raise ValidationError("Agreement signature date can't be in the future")

    def validate_period(self, data, value):
        if data.get("status") == "active":
            if not value:
                raise ValidationError("Period is required for agreement signing.")
            if not value.startDate or not value.endDate:
                raise ValidationError("startDate and endDate are required in agreement.period.")

            calculated_end_date = value.startDate + MAX_AGREEMENT_PERIOD
            if value.endDate > calculated_end_date:
                raise ValidationError(
                    f"Agreement period can't be greater than {duration_isoformat(MAX_AGREEMENT_PERIOD)}."
                )


# --- CFA selection: source agreement (copied from the frameworks agreement) and its changes ---


def validate_cfa_selection_only_addend_or_only_factor(modifications):
    if modifications:
        changes_with_addend_and_factor = [m for m in modifications if m.addend and m.factor]
        if changes_with_addend_and_factor:
            raise ValidationError("Change with taxRate rationaleType, can have only factor or only addend")


def validate_cfa_selection_modifications_items_uniq(items, changes):
    for change in changes or []:
        modifications = change.modifications
        if modifications and change.rationaleType in (
            "taxRate",
            "itemPriceVariation",
            "thirdParty",
        ):
            agreement_items_id = {i.id for i in items or []}
            item_ids = {m.itemId for m in modifications if m.itemId in agreement_items_id}
            if len(item_ids) != len(modifications):
                raise ValidationError("Item id should be uniq for all modifications and one of agreement:items")


class CFASelectionChange(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["pending", "active", "cancelled"], default="pending")
    date = IsoDateTimeType(default=get_request_now)
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    dateSigned = IsoDateTimeType()
    agreementNumber = StringType()

    def validate_dateSigned(self, data, value):
        if value and value > get_request_now():
            raise ValidationError("Agreement signature date can't be in the future")


class CFASelectionUnitPriceModification(Model):
    itemId = StringType()
    factor = DecimalType(required=False, precision=-4, min_value=Decimal("0.0"))
    addend = DecimalType(required=False, precision=-2)


class CFASelectionChangeTaxRate(CFASelectionChange):
    rationaleType = StringType(default="taxRate")
    modifications = ListType(
        ModelType(CFASelectionUnitPriceModification, required=True),
        validators=[validate_cfa_selection_only_addend_or_only_factor],
    )


def validate_cfa_selection_item_price_variation_modifications(modifications):
    for modification in modifications:
        if modification.addend:
            raise ValidationError("Only factor is allowed for itemPriceVariation type of change")
        if not Decimal("0.9") <= modification.factor <= Decimal("1.1"):
            raise ValidationError("Modification factor should be in range 0.9 - 1.1")


class CFASelectionChangeItemPriceVariation(CFASelectionChange):
    rationaleType = StringType(default="itemPriceVariation")
    modifications = ListType(
        ModelType(CFASelectionUnitPriceModification, required=True),
        validators=[validate_cfa_selection_item_price_variation_modifications],
    )


def validate_cfa_selection_third_party_modifications(modifications):
    for modification in modifications:
        if modification.addend:
            raise ValidationError("Only factor is allowed for thirdParty type of change")


class CFASelectionChangeThirdParty(CFASelectionChange):
    rationaleType = StringType(default="thirdParty")
    modifications = ListType(
        ModelType(CFASelectionUnitPriceModification, required=True),
        validators=[validate_cfa_selection_third_party_modifications],
    )


def validate_cfa_selection_modifications_contracts_uniq(contracts, changes):
    for change in changes or []:
        modifications = change.modifications
        if modifications and change.rationaleType == "partyWithdrawal":
            agreement_contracts_id = {i.id for i in contracts or []}
            contracts_ids = {c.contractId for c in modifications if c.contractId in agreement_contracts_id}
            if len(contracts_ids) != len(modifications):
                raise ValidationError("Contract id should be uniq for all modifications and one of agreement:contracts")


class CFASelectionContractModification(Model):
    itemId = StringType()
    contractId = StringType(required=True)


class CFASelectionChangePartyWithdrawal(CFASelectionChange):
    rationaleType = StringType(default="partyWithdrawal")
    modifications = ListType(
        ModelType(CFASelectionContractModification, required=True),
    )


class CFASelectionPatchAgreement(Model):
    id = MD5Type()
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    features = ListType(ModelType(CFASelectionFeature, required=True), validators=[validate_uniq_code])
    items = ListType(ModelType(TechFeatureItem, required=True))
    period = ModelType(Period)
    status = StringType(choices=["pending", "active", "cancelled", "terminated"])
    contracts = ListType(ModelType(CFASelectionAgreementContract, required=True))
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    terminationDetails = StringType()
    tender_id = MD5Type()
    dateModified = IsoDateTimeType()
    mode = StringType(choices=["test"])
    numberOfContracts = IntType()
    owner = StringType()
    procuringEntity = ModelType(ProcuringEntity)
    changes = ListType(
        PolyModelType(
            (
                CFASelectionChangeTaxRate,
                CFASelectionChangeItemPriceVariation,
                CFASelectionChangePartyWithdrawal,
                CFASelectionChangeThirdParty,
            ),
            claim_function=get_change_class,
        ),
    )

    def validate_changes(self, data, changes):
        validate_cfa_selection_modifications_items_uniq(data.get("items"), changes)
        validate_cfa_selection_modifications_contracts_uniq(data.get("contracts"), changes)

    def validate_contracts(self, data, contracts):
        validate_cfa_selection_parameter_contracts(data.get("features"), contracts)


class CFASelectionAgreement(CFASelectionPatchAgreement):
    id = MD5Type(required=True)
    documents = BaseType()
