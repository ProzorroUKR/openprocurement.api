from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.state.tender_details import (
    PQTenderDetailsState,
)


@resource(
    name=f"{PQ}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=PQ,
    description=f"{PQ} tenders",
    accept="application/json",
)
class PriceQuotationTenderResource(TendersResource):
    state_class = PQTenderDetailsState
