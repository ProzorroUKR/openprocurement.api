# -*- coding: utf-8 -*-
from openprocurement.tender.openua.interfaces import ITenderUA
from openprocurement.api.utils import opresource, json_view
from openprocurement.api.views.tender import TenderResource


def isTenderUA(info, request):
    if ITenderUA.providedBy(info):
        return True

    # on route get
    if isinstance(info, dict) and info.get('match') and 'tender_id' in info['match']:
        return ITenderUA.providedBy(request._tender)

    if hasattr(info, "__parent__"):
        while hasattr(info, "__parent__") and info.__parent__:
            if ITenderUA.providedBy(info.__parent__):
                return True

    return False  # do not handle unknown locations


@opresource(name='TenderUA',
            path='/tenders/{tender_id}',
            custom_predicates=(isTenderUA,),
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderUAResource(TenderResource):
    """ Resource handler for TenderUA """

    @json_view(permission='view_tender')
    def collection_get(self):
        1/0  # never happens
