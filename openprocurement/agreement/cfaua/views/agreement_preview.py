# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    APIResource,
    raise_operation_error
)
from openprocurement.agreement.core.resource import agreements_resource

from openprocurement.agreement.cfaua.models.modification import UnitPriceModification


def apply_modifications(request, agreement):
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
                        raise_operation_error(request, "unitPrice:value:amount can't be equal or less than 0.")
            else:
                for unit_price in unit_prices:
                    unit_price.value.amount *= modification.factor
        else:
            for contract in agreement.contract:
                if contract.id == modification.contractId:
                    contract.status = 'unsuccessful'
                    break


@agreements_resource(name='cfaua.AgreementPreview',
                     path='/agreements/{agreement_id}/preview',
                     agreementType='cfaua',
                     description='Agreements resource')
class AgreementPreviewResource(APIResource):

    @json_view(permission='view_agreement')
    def get(self):
        if not self.context.changes or self.context.changes[-1]['status'] != 'pending':
            return {"data": self.context.serialize("view")}
        apply_modifications(self.request, self.context)
        return {"data": self.context.serialize("view")}