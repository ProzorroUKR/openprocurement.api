from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_item_owner,
    validate_input_data,
    validate_patch_data,
    validate_award_with_lot_cancellation_in_pending,
)
from openprocurement.tender.limited.procedure.models.award import (
    PostReportingAward, PatchReportingAward, ReportingAward,
    PostNegotiationAward, PatchNegotiationAward, NegotiationAward,
)
from openprocurement.tender.limited.procedure.validation import (
    validate_award_operation_not_in_active_status,
    validate_create_new_award,
    validate_lot_cancellation,
    validate_create_new_award_with_lots,
    validate_award_same_lot_id,
)
from openprocurement.tender.limited.procedure.state.award import (
    ReportingAwardState,
    NegotiationAwardState,
    NegotiationQuickAwardState,
)
from pyramid.security import Allow, Everyone
from cornice.resource import resource


@resource(
    name="reporting:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="reporting",
)
class ReportingAwardResource(TenderAwardResource):
    state_class = ReportingAwardState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_award"),
            (Allow, "g:brokers", "edit_award"),
            (Allow, "g:brokers", "upload_award_documents"),
            (Allow, "g:brokers", "edit_award_documents"),

            (Allow, "g:admins", "create_award"),
            (Allow, "g:admins", "edit_award"),
            (Allow, "g:admins", "upload_award_documents"),
            (Allow, "g:admins", "edit_award_documents"),

            (Allow, "g:bots", "upload_award_documents"),
        ]
        return acl

    @json_view(
        content_type="application/json",
        permission="create_award",
        validators=(
            unless_admins(
                validate_item_owner("tender")
            ),
            validate_input_data(PostReportingAward),
            validate_award_operation_not_in_active_status,
            validate_create_new_award,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(
                validate_item_owner("tender")
            ),
            validate_input_data(PatchReportingAward),
            validate_patch_data(ReportingAward, item_name="award"),
            validate_award_operation_not_in_active_status,
        ),
    )
    def patch(self):
        return super().patch()


@resource(
    name="negotiation:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="negotiation",
)
class NegotiationAwardResource(TenderAwardResource):
    state_class = NegotiationAwardState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_award"),
            (Allow, "g:brokers", "edit_award"),
            (Allow, "g:brokers", "upload_award_documents"),
            (Allow, "g:brokers", "edit_award_documents"),

            (Allow, "g:admins", "create_award"),
            (Allow, "g:admins", "edit_award"),
            (Allow, "g:admins", "upload_award_documents"),
            (Allow, "g:admins", "edit_award_documents"),

            (Allow, "g:bots", "upload_award_documents"),
        ]
        return acl

    @json_view(
        content_type="application/json",
        permission="create_award",
        validators=(
            unless_admins(
                validate_item_owner("tender")
            ),
            validate_input_data(PostNegotiationAward),
            validate_award_operation_not_in_active_status,
            validate_award_with_lot_cancellation_in_pending,
            validate_lot_cancellation,
            validate_create_new_award_with_lots,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_award",
        validators=(
            unless_admins(
                validate_item_owner("tender")
            ),
            validate_input_data(PatchNegotiationAward),
            validate_patch_data(NegotiationAward, item_name="award"),
            validate_award_with_lot_cancellation_in_pending,
            validate_award_operation_not_in_active_status,
            validate_lot_cancellation,
            validate_award_same_lot_id,
        ),
    )
    def patch(self):
        return super().patch()


@resource(
    name="negotiation.quick:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="negotiation.quick",
)
class NegotiationQuickAwardResource(NegotiationAwardResource):
    state_class = NegotiationQuickAwardState
