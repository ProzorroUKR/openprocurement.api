# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context
from openprocurement.api.validation import validate_data
from openprocurement.tender.belowthreshold.utils import  check_document


def validate_bid_data(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'bid_id': '__new__'})
    model = type(request.tender).bids.model_class
    bid = validate_data(request, model)
    validated_bid = request.validated.get('bid')
    if validated_bid:
        if any([key == 'documents' or 'Documents' in key for key in validated_bid.keys()]):
            bid_documents = validate_bid_documents(request)
            if not bid_documents:
                return
            for documents_type, documents in bid_documents.items():
                validated_bid[documents_type] = documents
    return bid


def validate_patch_bid_data(request):
    model = type(request.tender).bids.model_class
    return validate_data(request, model, True)


def validate_award_data(request):
    update_logging_context(request, {'award_id': '__new__'})
    model = type(request.tender).awards.model_class
    return validate_data(request, model)


def validate_patch_award_data(request):
    model = type(request.tender).awards.model_class
    return validate_data(request, model, True)


def validate_cancellation_data(request):
    update_logging_context(request, {'cancellation_id': '__new__'})
    model = type(request.tender).cancellations.model_class
    return validate_data(request, model)


def validate_patch_cancellation_data(request):
    model = type(request.tender).cancellations.model_class
    return validate_data(request, model, True)


def validate_contract_data(request):
    update_logging_context(request, {'contract_id': '__new__'})
    model = type(request.tender).contracts.model_class
    return validate_data(request, model)


def validate_patch_contract_data(request):
    model = type(request.tender).contracts.model_class
    return validate_data(request, model, True)


def validate_bid_documents(request):
    bid_documents = [key for key in request.validated['bid'].keys() if key == 'documents' or 'Documents' in key]
    documents = {}
    for doc_type in bid_documents:
        documents[doc_type] = []
        for document in request.validated['bid'][doc_type]:
            model = getattr(type(request.validated['bid']), doc_type).model_class
            document = model(document)
            document.validate()
            route_kwargs = {'bid_id': request.validated['bid'].id}
            document = check_document(request, document, doc_type, route_kwargs)
            documents[doc_type].append(document)
    return documents
