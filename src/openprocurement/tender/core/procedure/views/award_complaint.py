from openprocurement.api.procedure.validation import validate_request_by_state
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintState,
)
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseComplaintGetResource,
    BaseComplaintWriteResource,
    resolve_complaint,
)


class AwardComplaintGetResource(BaseComplaintGetResource):
    item_name = "award"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_complaint(request, context="award")


class AwardComplaintWriteResource(BaseComplaintWriteResource):
    state_class = AwardComplaintState
    item_name = "award"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_complaint(request, context="award")

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(validate_request_by_state,),
    )
    def collection_post(self):
        return super().collection_post()
