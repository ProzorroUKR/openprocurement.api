# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context, error_handler
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.contracting.api.models import Contract, Change

OPERATIONS = {"POST": "add", "PATCH": "update", "PUT": "update"}

def validate_contract_data(request):
    update_logging_context(request, {'contract_id': '__new__'})
    data = request.validated['json_data'] = validate_json_data(request)
    model = request.contract_from_data(data, create=False)
    if hasattr(request, 'check_accreditation') and not request.check_accreditation(model.create_accreditation):
        request.errors.add('contract', 'accreditation', 'Broker Accreditation level does not permit contract creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    return validate_data(request, model, data=data)


def validate_patch_contract_data(request):
    return validate_data(request, Contract, True)


def validate_change_data(request):
    update_logging_context(request, {'change_id': '__new__'})
    data = validate_json_data(request)
    return validate_data(request, Change, data=data)


def validate_patch_change_data(request):
    return validate_data(request, Change, True)

# changes
def validate_contract_change_add_not_in_allowed_contract_status(request):
    contract = request.validated['contract']
    if contract.status != 'active':
        request.errors.add('body', 'data', 'Can\'t add contract change in current ({}) contract status'.format(contract.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_create_contract_change(request):
    contract = request.validated['contract']
    if contract.changes and contract.changes[-1].status == 'pending':
        request.errors.add('body', 'data', 'Can\'t create new contract change while any (pending) change exists')
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_contract_change_update_not_in_allowed_change_status(request):
    change = request.validated['change']
    if change.status == 'active':
        request.errors.add('body', 'data', 'Can\'t update contract change in current ({}) status'.format(change.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_contract_change_status(request):
    data = request.validated['data']
    if not data.get("dateSigned", ''):
        request.errors.add('body', 'data', 'Can\'t update contract change status. \'dateSigned\' is required.')
        request.errors.status = 403
        raise error_handler(request.errors)

# contract
def validate_contract_update_not_in_allowed_status(request):
    contract = request.validated['contract']
    if request.authenticated_role != 'Administrator' and contract.status != 'active':
        request.errors.add('body', 'data', 'Can\'t update contract in current ({}) status'.format(contract.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_terminate_contract_without_amountPaid(request):
    contract = request.validated['contract']
    if contract.status == 'terminated' and not contract.amountPaid:
        request.errors.add('body', 'data', 'Can\'t terminate contract while \'amountPaid\' is not set')
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_credentials_generate(request):
    contract = request.validated['contract']
    if contract.status != "active":
        request.errors.add('body', 'data', 'Can\'t generate credentials in current ({}) contract status'.format(contract.status))
        request.errors.status = 403
        raise error_handler(request.errors)

# contract document
def validate_contract_document_operation_not_in_allowed_contract_status(request):
    if request.validated['contract'].status != 'active':
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) contract status'.format(OPERATIONS.get(request.method), request.validated['contract'].status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_add_document_to_active_change(request):
    data = request.validated['data']
    if "relatedItem" in data and data.get('documentOf') == 'change':
        if not [1 for c in request.validated['contract'].changes if c.id == data['relatedItem'] and c.status == 'pending']:
            request.errors.add('body', 'data', 'Can\'t add document to \'active\' change')
            request.errors.status = 403
            raise error_handler(request.errors)
