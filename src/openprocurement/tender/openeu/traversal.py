# -*- coding: utf-8 -*-
from openprocurement.tender.core.traversal import Root, get_item


def qualifications_factory(request):
    request.validated['tender_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('tender_id'):
        return root
    request.validated['tender_id'] = request.matchdict['tender_id']
    tender = request.tender
    tender.__parent__ = root
    request.validated['tender'] = request.validated['db_doc'] = tender
    request.validated['tender_status'] = tender.status
    if request.method != 'GET':
        request.validated['tender_src'] = tender.serialize('plain')
    if request.matchdict.get('qualification_id'):
        qualification = get_item(tender, 'qualification', request)
        if request.matchdict.get('complaint_id'):
            complaint = get_item(qualification, 'complaint', request)
            if request.matchdict.get('document_id'):
                return get_item(complaint, 'document', request)
            else:
                return complaint
        elif request.matchdict.get('document_id'):
            return get_item(qualification, 'document', request)
        else:
            return qualification
    request.validated['id'] = request.matchdict['tender_id']
    return tender


def get_document(parent, key, request):
    request.validated['document_id'] = request.matchdict['document_id']

    attr = key.split('_')
    attr = attr[0] + attr[1].capitalize() + 's'
    items = [i for i in getattr(parent, attr, []) if i.id == request.matchdict['document_id']]
    if not items:
        from openprocurement.api.utils import error_handler
        request.errors.add('url', 'document_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)
    else:
        if 'document' in key:
            request.validated['documents'] = items
        item = items[-1]
        request.validated['document'] = item

        request.validated['id'] = request.matchdict['document_id']
        item.__parent__ = parent
        return item


def handle_root(request):
    request.validated['tender_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('tender_id'):
        return root
    request.validated['tender_id'] = request.matchdict['tender_id']
    tender = request.tender
    tender.__parent__ = root
    request.validated['tender'] = request.validated['db_doc'] = tender
    request.validated['tender_status'] = tender.status
    if request.method != 'GET':
        request.validated['tender_src'] = tender.serialize('plain')


def bid_financial_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated['tender']
    if request.matchdict.get('bid_id'):
        bid = get_item(tender, 'bid', request)
        if request.matchdict.get('document_id'):
            return get_document(bid, 'financial_document', request)
        else:
            return bid


def bid_eligibility_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated['tender']
    if request.matchdict.get('bid_id'):
        bid = get_item(tender, 'bid', request)
        if request.matchdict.get('document_id'):
            return get_document(bid, 'eligibility_document', request)
        else:
            return bid


def bid_qualification_documents_factory(request):
    response = handle_root(request)
    if response:
        return response
    tender = request.validated['tender']
    if request.matchdict.get('bid_id'):
        bid = get_item(tender, 'bid', request)
        if request.matchdict.get('document_id'):
            return get_document(bid, 'qualification_document', request)
        else:
            return bid
