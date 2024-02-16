from openprocurement.historical.core.utils import APIHistoricalResource
from openprocurement.historical.tender.utils import tenders_history_resource


@tenders_history_resource(name="TenderHistory", path="/tenders/{doc_id}/historical")
class TenderHistoryResource(APIHistoricalResource):
    pass
