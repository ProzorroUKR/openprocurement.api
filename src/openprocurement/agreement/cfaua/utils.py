# -*- coding: utf-8 -*-
from zope.component import queryUtility
from openprocurement.api.utils import raise_operation_error
from openprocurement.agreement.cfaua.constants import MIN_BIDS_NUMBER
from openprocurement.agreement.cfaua.interfaces import IChange
from openprocurement.agreement.cfaua.models.modification import UnitPriceModification


def apply_modifications(request, agreement, save=False):
    warnings = []
    if not save:
        agreement = agreement.__class__(agreement.serialize("view"))
    if not agreement.changes[-1].modifications:
        return
    for modification in agreement.changes[-1].modifications:
        if isinstance(modification, UnitPriceModification):
            unit_prices = [
                unit_price
                for contract in agreement.contracts
                for unit_price in contract.unitPrices
                if unit_price.relatedItem == modification.itemId
            ]

            for unit_price in unit_prices:
                if modification.addend:
                    unit_price.value.amount += modification.addend
                if modification.factor is not None:
                    unit_price.value.amount *= modification.factor
                if unit_price.value.amount <= 0:
                    raise_operation_error(request, "unitPrice:value:amount can't be equal or less than 0.")
        else:
            for contract in agreement.contracts:
                if contract.id == modification.contractId:
                    contract.status = "unsuccessful"
                    break
    if agreement.get_active_contracts_count() < MIN_BIDS_NUMBER:
        warnings.append("Min active contracts in FrameworkAgreement less than {}.".format(MIN_BIDS_NUMBER))
    return warnings
