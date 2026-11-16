from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.pricequotation.procedure.state.tender_details import (
    PQTenderDetailsState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description=f"{ProcurementMethodType.PRICE_QUOTATION} tenders",
    accept="application/json",
)
class PriceQuotationTenderResource(TendersResource):
    state_class = PQTenderDetailsState
