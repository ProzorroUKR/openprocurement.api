# -*- coding: utf-8 -*-
from openprocurement.api.traversal import Root


def tender_historical_factory(request):
    request.validated['tender_src'] = {}
    root = Root(request)
    if not request.matchdict or not request.matchdict.get('tender_id'):
        return root
    request.validated['tender_id'] = request.matchdict['tender_id']
    tender = request.historical_tender
    tender.__parent__ = root
    request.validated['tender'] = tender
    request.validated['id'] = request.matchdict['tender_id']
    return tender
