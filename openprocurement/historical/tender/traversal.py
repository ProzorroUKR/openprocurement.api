from openprocurement.historical.core.utils import Root


def historical_tender_factory(request):
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('doc_id'):
        return root
    request.validated['tender_id'] = request.matchdict['doc_id']
    doc = request.tender_from_data(request.extract_doc_versioned('Tender'))
    doc.__parent__ = root
    request.validated['tender'] = doc
    request.validated['id'] = request.matchdict['doc_id']
    request.validated['tender_status'] = doc.status
    return doc
