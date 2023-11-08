from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintState,
)
from openprocurement.tender.core.procedure.views.qualification import resolve_qualification
from openprocurement.tender.core.procedure.serializers.complaint import TenderComplaintSerializer
from openprocurement.tender.core.procedure.models.complaint import PostQualificationComplaint
from openprocurement.tender.core.procedure.views.complaint import (
    resolve_complaint,
    BaseComplaintGetResource,
    BaseComplaintWriteResource,
)
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_any_bid_owner,
    validate_input_data,
    validate_data_documents,
)


class QualificationComplaintGetResource(BaseComplaintGetResource):
    serializer_class = TenderComplaintSerializer
    item_name = "qualification"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_qualification(request)
            resolve_complaint(request, context="qualification")


class QualificationComplaintWriteResource(BaseComplaintWriteResource):
    serializer_class = TenderComplaintSerializer
    state_class = QualificationComplaintState
    item_name = "qualification"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_qualification(request)
            resolve_complaint(request, context="qualification")

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(
            validate_input_data(PostQualificationComplaint),
            unless_admins(
                validate_any_bid_owner(statuses=("active", "unsuccessful"))
            ),
            validate_data_documents(route_key="complaint_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
