from cornice.resource import resource
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.procedure.models.qualification import (
    PatchQualification,
    Qualification,
)
from openprocurement.tender.core.procedure.serializers.qualification import (
    QualificationSerializer,
)
from openprocurement.tender.core.procedure.state.qualification import QualificationState
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    validate_cancelled_qualification_update,
    validate_operation_with_lot_cancellation_in_pending,
    validate_qualification_update_not_in_pre_qualification,
    validate_update_status_before_milestone_due_date,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


def resolve_qualification(request):
    match_dict = request.matchdict
    if match_dict.get("qualification_id"):
        qualification_id = match_dict["qualification_id"]
        qualification = get_items(request, request.validated["tender"], "qualifications", qualification_id)
        request.validated["qualification"] = qualification[0]


@resource(
    name="Tender Qualification",
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    description="Tender Qualification",
)
class TenderQualificationResource(TenderBaseResource):
    # model_class = Qualification
    serializer_class = QualificationSerializer
    state_class = QualificationState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "edit_qualification"),
            (Allow, "g:bots", "edit_qualification"),
            # (Allow, "g:bots", "create_qualification"),
            # (Allow, "g:framework_owner", "edit_qualification"),
            (Allow, "g:Administrator", "edit_qualification"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_qualification(request)

    @json_view(permission="view_tender")
    def collection_get(self):
        """List qualifications"""
        tender = self.request.validated["tender"]
        data = tuple(self.serializer_class(qualification).data for qualification in tender.get("qualifications", []))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the qualification"""
        data = self.serializer_class(self.request.validated["qualification"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(PatchQualification),
            validate_patch_data(Qualification, item_name="qualification"),
            validate_qualification_update_not_in_pre_qualification,
            validate_operation_with_lot_cancellation_in_pending("qualification"),
            validate_cancelled_qualification_update,
            validate_update_status_before_milestone_due_date,
        ),
        permission="edit_qualification",
    )
    def patch(self):
        """Post a qualification resolution"""
        updated = self.request.validated["data"]
        if updated:
            qualification = self.request.validated["qualification"]
            set_item(self.request.validated["tender"], "qualifications", qualification["id"], updated)
            self.state.qualification_on_patch(qualification, updated)
            self.state.always(self.request.validated["tender"])
            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated tender qualification {}".format(qualification["id"]),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_qualification_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
