# -*- coding: utf-8 -*-
from hashlib import sha512
from openprocurement.api.utils import update_logging_context
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.relocation.api.models import Transfer


def validate_transfer_data(request):
    update_logging_context(request, {'transfer_id': '__new__'})
    data = validate_json_data(request)
    if data is None:
        return
    model = Transfer
    return validate_data(request, model, data=data)


def validate_ownership_data(request):
    if request.errors:
        return
    data = validate_json_data(request)

    for field in ['id', 'transfer']:
        if not data.get(field):
            request.errors.add('body', field, 'This field is required.')
    if request.errors:
        request.errors.status = 422
        return
    request.validated['ownership_data'] = data


def validate_accreditation_level(request, obj, level_name):
    level = getattr(type(obj), level_name)
    if not request.check_accreditations(level):
        request.errors.add(
            'procurementMethodType', 'accreditation',
            'Broker Accreditation level does not permit ownership change')
        request.errors.status = 403
        return

    if obj.get('mode', None) is None and request.check_accreditations(('t',)):
        request.errors.add(
            'procurementMethodType', 'mode',
            'Broker Accreditation level does not permit ownership change')
        request.errors.status = 403
        return


def validate_tender_accreditation_level(request):
    validate_accreditation_level(request, request.validated['tender'], 'transfer_accreditations' if hasattr(
        request.validated['tender'], 'transfer_accreditations'
    ) else 'create_accreditations')


def validate_contract_accreditation_level(request):
    validate_accreditation_level(request, request.validated['contract'], 'create_accreditations')


def validate_plan_accreditation_level(request):
    validate_accreditation_level(request, request.validated['plan'], 'create_accreditations')


def validate_agreement_accreditation_level(request):
    validate_accreditation_level(request, request.validated['agreement'], 'create_accreditations')


def validate_transfer_token(request, obj):
    if request.errors:
        return
    if obj.transfer_token != sha512(request.validated['ownership_data']['transfer']).hexdigest():
        request.errors.add('body', 'transfer', 'Invalid transfer')
        request.errors.status = 403


def validate_tender_transfer_token(request):
    validate_transfer_token(request, request.validated['tender'])


def validate_contract_transfer_token(request):
    validate_transfer_token(request, request.validated['contract'])


def validate_plan_transfer_token(request):
    validate_transfer_token(request, request.validated['plan'])


def validate_agreement_transfer_token(request):
    validate_transfer_token(request, request.validated['agreement'])


def validate_tender(request):
    if request.errors:
        return
    tender = request.validated['tender']
    if tender.status in ['complete', 'unsuccessful', 'cancelled']:
        request.errors.add(
            'body', 'data',
            'Can\'t update credentials in current ({}) '
            'tender status'.format(tender.status))
        request.errors.status = 403


def validate_contract(request):
    if request.errors:
        return
    contract = request.validated['contract']
    if contract.status != "active":
        request.errors.add(
            'body', 'data',
            'Can\'t update credentials in current ({}) '
            'contract status'.format(contract.status))
        request.errors.status = 403


def validate_agreement(request):
    if request.errors:
        return
    agreement = request.validated['agreement']
    if agreement.status != "active":
        request.errors.add(
            'body', 'data',
            'Can\'t update credentials in current ({}) '
            'agreement status'.format(agreement.status))
        request.errors.status = 403
