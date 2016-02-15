# -*- coding: utf-8 -*-
from openprocurement.api.traversal import Root, get_item


def qualifications_factory(request):
    request.validated['tender_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('tender_id'):
        return root
    request.validated['tender_id'] = request.matchdict['tender_id']
    tender = request.tender
    tender.__parent__ = root
    request.validated['tender'] = tender
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
