from schematics.types import BaseType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType, PolyModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.procedure.validation import validate_features_uniq
from openprocurement.api.utils import get_change_class
from openprocurement.tender.cfaselectionua.procedure.models.agreement_contract import (
    AgreementContract,
)
from openprocurement.tender.cfaselectionua.procedure.models.change import (
    ChangeItemPriceVariation,
    ChangePartyWithdrawal,
    ChangeTaxRate,
    ChangeThirdParty,
    validate_modifications_contracts_uniq,
    validate_modifications_items_uniq,
)
from openprocurement.tender.cfaselectionua.procedure.models.feature import Feature
from openprocurement.tender.cfaselectionua.procedure.models.item import Item
from openprocurement.tender.cfaselectionua.procedure.models.organization import (
    ProcuringEntity,
)
from openprocurement.tender.cfaselectionua.procedure.models.parameter_contract import (
    validate_parameter_contracts,
)


class PatchAgreement(Model):
    id = MD5Type()
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    items = ListType(ModelType(Item, required=True))
    period = ModelType(Period)
    status = StringType(choices=["pending", "active", "cancelled", "terminated"])
    contracts = ListType(ModelType(AgreementContract, required=True))
    title = StringType()
    title_en = StringType()
    title_ru = StringType()

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
                ChangeTaxRate,
                ChangeItemPriceVariation,
                ChangePartyWithdrawal,
                ChangeThirdParty,
            ),
            claim_function=get_change_class,
        ),
    )

    def validate_changes(self, data, changes):
        validate_modifications_items_uniq(data.get("items"), changes)
        validate_modifications_contracts_uniq(data.get("contracts"), changes)

    def validate_contracts(self, data, contracts):
        validate_parameter_contracts(data.get("features"), contracts)


class Agreement(PatchAgreement):
    id = MD5Type(required=True)
    documents = BaseType()
