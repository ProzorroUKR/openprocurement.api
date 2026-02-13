from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.cancellation import CancellationState
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)


@resource(
    name="complexAsset.arma:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellations",
)
class CancellationResource(BaseCancellationResource):
    state_class = CancellationState
