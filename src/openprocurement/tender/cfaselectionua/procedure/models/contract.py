from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.context import get_now
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.cfaselectionua.procedure.models.document import (
    ContractDocument,
)
from openprocurement.tender.cfaselectionua.procedure.models.item import ContractItem
from openprocurement.tender.cfaselectionua.procedure.models.organization import (
    BusinessOrganization,
)
from openprocurement.tender.core.procedure.models.contract import (
    Contract as BaseContract,
)
from openprocurement.tender.core.procedure.models.contract import ContractValue
from openprocurement.tender.core.procedure.models.contract import (
    PatchContract as BasePatchContract,
)
from openprocurement.tender.core.procedure.models.contract import (
    PatchContractSupplier as BasePatchContractSupplier,
)
from openprocurement.tender.core.procedure.models.contract import (
    validate_item_unit_values,
)


class Contract(BaseContract):
    value = ModelType(ContractValue)
    awardID = StringType(required=True)
    documents = ListType(ModelType(ContractDocument, required=True))
    items = ListType(ModelType(ContractItem, required=True))
    suppliers = ListType(ModelType(BusinessOrganization), min_size=1, max_size=1)

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError("Contract signature date can't be in the future")


class PostContract(Contract):
    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


class PatchContract(BasePatchContract):
    items = ListType(ModelType(ContractItem, required=True))

    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


class PatchContractSupplier(BasePatchContractSupplier):
    pass
