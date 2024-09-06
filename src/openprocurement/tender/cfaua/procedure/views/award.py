from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.cfaua.procedure.models.award import Award, PatchAward
from openprocurement.tender.cfaua.procedure.serializers.tender import (
    CFAUATenderSerializer,
)
from openprocurement.tender.cfaua.procedure.state.award import AwardState
from openprocurement.tender.cfaua.procedure.validation import (
    validate_update_award_in_not_allowed_status,
)
from openprocurement.tender.core.procedure.validation import (
    validate_award_with_lot_cancellation_in_pending,
    validate_update_award_only_for_active_lots,
    validate_update_award_status_before_milestone_due_date,
    validate_update_award_with_accepted_complaint,
)
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
    state_class = AwardState

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(PatchAward),
            validate_patch_data(Award, item_name="award"),
            validate_award_with_lot_cancellation_in_pending,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
            validate_update_award_with_accepted_complaint,
            validate_update_award_status_before_milestone_due_date,
        ),
    )
    def patch(self):
        return super().patch()

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
