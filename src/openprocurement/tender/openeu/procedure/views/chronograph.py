from cornice.resource import resource

from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


@resource(
    name="aboveThresholdEU:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU chronograph",
)
class OpenEUChronographResource(TenderChronographResource):
    state_class = BaseOpenEUTenderState
