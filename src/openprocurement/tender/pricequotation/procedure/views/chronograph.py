from cornice.resource import resource

from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


@resource(
    name=f"{PQ}:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="priceQuotation",
    description="Tender chronograph",
)
class PQChronographResource(TenderChronographResource):
    state_class = PriceQuotationTenderState
