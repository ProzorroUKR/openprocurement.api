from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name="complexAsset.arma:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender chronograph",
)
class ChronographResource(TenderChronographResource):
    state_class = TenderState
