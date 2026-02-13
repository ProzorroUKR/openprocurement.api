from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.lot import LotState
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="complexAsset.arma:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="ARMA lots",
)
class LotResource(TenderLotResource):
    state_class = LotState
