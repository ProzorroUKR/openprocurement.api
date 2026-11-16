from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


@resource(
    name="esco:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.ESCO,
    description="Tender chronograph",
)
class ESCOChronographResource(TenderChronographResource):
    state_class = ESCOTenderState
