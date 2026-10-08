from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.serializers.tender import (
    CFAUATenderSerializer,
)
from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name="closeFrameworkAgreementUA:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="closeFrameworkAgreementUA tenders",
    accept="application/json",
)
class CFAUATenderResource(TendersResource):
    serializer_class = CFAUATenderSerializer
    state_class = CFAUATenderDetailsState
