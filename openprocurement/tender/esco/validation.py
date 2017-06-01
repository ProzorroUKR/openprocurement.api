# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error


def validate_update_contract_value(request):
    tender = request.validated['tender']
    data = request.validated['data']
    if data.get('value'):
        for ro_attr in ('valueAddedTaxIncluded', 'currency'):
            if data['value'][ro_attr] != getattr(request.context.value, ro_attr):
                raise_operation_error(request, 'Can\'t update {} for contract value'.format(ro_attr))
        award = [a for a in tender.awards if a.id == request.context.awardID][0]
        if data['value']['amount'] != award.value.amount:
            raise_operation_error(request, 'Value amount should be equal to awarded amount ({})'.format(award.value.amount))
