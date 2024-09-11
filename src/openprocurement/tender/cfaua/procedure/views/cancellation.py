from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.cfaua.procedure.serializers.tender import (
    CFAUATenderSerializer,
)
from openprocurement.tender.cfaua.procedure.state.cancellation import (
    CFAUACancellationState,
)
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)
from openprocurement.tender.core.utils import context_view


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellations",
)
class CFAUACancellationResource(BaseCancellationResource):
    state_class = CFAUACancellationState

    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": CFAUATenderSerializer,
        }
    )
    def get(self):
        return super().get()
