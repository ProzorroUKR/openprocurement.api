from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.cfaua.procedure.serializers.agreement import (
    AgreementSerializer,
)
from openprocurement.tender.cfaua.procedure.state.agreement import CFAUAAgreementState
from openprocurement.tender.core.procedure.views.agreement import (
    TenderAgreementResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Agreements",
    collection_path="/tenders/{tender_id}/agreements",
    path="/tenders/{tender_id}/agreements/{agreement_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU agreements",
)
class CFAUAAgreementResource(TenderAgreementResource):
    serializer_class = AgreementSerializer
    state_class = CFAUAAgreementState

    @json_view(
        content_type="application/json",
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
