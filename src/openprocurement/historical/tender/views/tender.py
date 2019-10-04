from openprocurement.historical.tender.utils import tenders_history_resource
from openprocurement.historical.core.utils import APIHistoricalResource


@tenders_history_resource(name="TenderHistory", path="/tenders/{doc_id}/historical")
class TenderHistoryResource(APIHistoricalResource):
    pass
