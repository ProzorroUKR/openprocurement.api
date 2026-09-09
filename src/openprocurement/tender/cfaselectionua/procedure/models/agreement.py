from schematics.types import BaseType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType, PolyModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.utils import get_change_class
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.cfaselectionua.procedure.models.agreement_contract import CFASelectionAgreementContract
from openprocurement.tender.cfaselectionua.procedure.models.feature import CFASelectionFeature
from openprocurement.tender.core.procedure.models.agreement import (
    AgreementChange,
    ContractModification,
    UnitPriceModification,
    validate_cfa_selection_modifications_contracts_uniq,
    validate_cfa_selection_modifications_items_uniq,
    validate_item_price_variation_modifications,
    validate_only_addend_or_only_factor,
    validate_third_party_modifications,
)
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.milestone import Milestone
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.parameter import validate_cfa_selection_parameter_contracts


class CFASelectionChangeTaxRate(AgreementChange):
    rationaleType = StringType(default="taxRate")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_only_addend_or_only_factor],
    )


class CFASelectionChangeItemPriceVariation(AgreementChange):
    rationaleType = StringType(default="itemPriceVariation")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_item_price_variation_modifications],
    )


class CFASelectionChangeThirdParty(AgreementChange):
    rationaleType = StringType(default="thirdParty")
    modifications = ListType(
        ModelType(UnitPriceModification, required=True),
        validators=[validate_third_party_modifications],
    )


class CFASelectionChangePartyWithdrawal(AgreementChange):
    rationaleType = StringType(default="partyWithdrawal")
    modifications = ListType(
        ModelType(ContractModification, required=True),
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
    items = ListType(ModelType(Item, required=True))
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
