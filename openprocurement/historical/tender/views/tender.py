from openprocurement.historical.tender.utils import tenders_history_resource
from openprocurement.api.utils import json_view, APIResource


@tenders_history_resource(name='TenderHistory',
                          path='/tenders/{tender_id}/historical',
                          description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderHistoryResource(APIResource):

    @json_view(permission="view_tender")
    def get(self):
        tender = self.request.validated['tender']
        return {'data': tender.serialize(tender.status)}
