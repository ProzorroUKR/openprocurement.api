from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PQTenderState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description="Tender chronograph",
)
class PQChronographResource(TenderChronographResource):
    state_class = PQTenderState
