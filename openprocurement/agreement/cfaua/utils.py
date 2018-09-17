# -*- coding: utf-8 -*-
from zope.component import queryUtility
from openprocurement.api.utils import raise_operation_error
from openprocurement.agreement.cfaua.interfaces import IChange
from openprocurement.agreement.cfaua.models.modification import UnitPriceModification


def get_change_class(instance, data):
    return queryUtility(IChange, data['rationaleType'])


def apply_modifications(request, agreement, save=False):
    if not save:
        agreement = agreement.__class__(agreement.serialize('view'))
    if not agreement.changes[-1].modifications:
        return
    for modification in agreement.changes[-1].modifications:
        if isinstance(modification, UnitPriceModification):
            unit_prices = [unit_price
                           for contract in agreement.contracts
                           for unit_price in contract.unitPrices
                           if unit_price.relatedItem == modification.itemId]
            if modification.addend:
                for unit_price in unit_prices:
                    unit_price.value.amount += modification.addend
                    if unit_price.value.amount <= 0:
                        raise_operation_error(request, u"unitPrice:value:amount can't be equal or less than 0.")
            else:
                for unit_price in unit_prices:
                    unit_price.value.amount *= modification.factor
        else:
            for contract in agreement.contracts:
                if contract.id == modification.contractId:
                    contract.status = 'unsuccessful'
                    break
