from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
)


class AgreementUUID(Model):
    id: MD5


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


def validate_cfa_selection_modifications_contracts_uniq(contracts, changes):
    for change in changes or []:
        modifications = change.modifications
        if modifications and change.rationaleType == "partyWithdrawal":
            agreement_contracts_id = {i.id for i in contracts or []}
            contracts_ids = {c.contractId for c in modifications if c.contractId in agreement_contracts_id}
            if len(contracts_ids) != len(modifications):
                raise ValidationError("Contract id should be uniq for all modifications and one of agreement:contracts")
