from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.serializers.complaint import (
    TenderComplaintSerializer,
)
from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimState,
)
from openprocurement.tender.core.procedure.views.claim import (
    BaseClaimResource,
    resolve_claim,
)
from openprocurement.tender.core.procedure.views.qualification import (
    resolve_qualification,
)


class QualificationClaimResource(BaseClaimResource):
    serializer_class = TenderComplaintSerializer
    state_class = QualificationClaimState
    item_name = "qualification"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_qualification(request)
            resolve_claim(request, context="qualification")

    @json_view(
        content_type="application/json",
        permission="create_claim",
    )
    def collection_post(self):
        return super().collection_post()
