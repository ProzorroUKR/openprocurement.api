from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.pricequotation.procedure.state.award import PQAwardState


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
)
class PQTenderAwardResource(TenderAwardResource):
    state_class = PQAwardState
