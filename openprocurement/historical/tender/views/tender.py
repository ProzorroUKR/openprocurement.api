from openprocurement.historical.tender.utils import (
    tenders_history_resource
)

from openprocurement.historical.core.utils import (
    get_route,
    call_view,
    return404
)

from openprocurement.api.utils import (
    json_view,
    APIResource
)


@tenders_history_resource(name='TenderHistory',
                          path='/tenders/{doc_id}/historical',
                          has_request_method='extract_doc_versioned',
                          description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderHistoryResource(APIResource):

    @json_view(permission="view_tender")
    def get(self):
        route = get_route(self.request)
        if route is None:
            return404(self.request, 'url', 'tender_id')
        return call_view(self.request, self.context, route)
