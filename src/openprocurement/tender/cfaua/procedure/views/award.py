from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.cfaua.procedure.serializers.tender import (
    CFAUATenderSerializer,
)
from openprocurement.tender.cfaua.procedure.state.award import CFAUAAwardState
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.core.utils import context_view


@resource(
    name="closeFrameworkAgreementUA:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender EU awards",
    procurementMethodType="closeFrameworkAgreementUA",
)
class UATenderAwardResource(TenderAwardResource):
    state_class = CFAUAAwardState

    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": (CFAUATenderSerializer, TENDER_MASK_MAPPING),
        }
    )
    def get(self):
        return super().get()
