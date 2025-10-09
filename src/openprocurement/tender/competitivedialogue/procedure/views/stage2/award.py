from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.models.award import (
    EUAward,
    EUPatchAward,
    EUPostAward,
    UAAward,
    UAPatchAward,
    UAPostAward,
)
from openprocurement.tender.core.procedure.validation import (
    validate_award_with_lot_cancellation_in_pending,
    validate_create_award_not_in_allowed_period,
    validate_create_award_only_for_active_lot,
    validate_update_award_in_not_allowed_status,
    validate_update_award_only_for_active_lots,
    validate_update_award_status_before_milestone_due_date,
)
from openprocurement.tender.openeu.procedure.views.award import EUTenderAwardResource
from openprocurement.tender.openua.procedure.views.award import UATenderAwardResource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Competitive Dialogue Stage 2 EU awards",
    procurementMethodType=STAGE_2_EU_TYPE,
)
class CDStage2EUTenderAwardResource(EUTenderAwardResource):
    @json_view(
        content_type="application/json",
        permission="create_award",  # admins only
        validators=(
            validate_input_data(EUPostAward),
            validate_create_award_not_in_allowed_period,
            validate_create_award_only_for_active_lot,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(
                EUPatchAward,
                none_means_remove=True,
            ),
            validate_patch_data_simple(EUAward, item_name="award"),
            validate_award_with_lot_cancellation_in_pending,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
            validate_update_award_status_before_milestone_due_date,
        ),
    )
    def patch(self):
        return super().patch()


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Competitive Dialogue Stage 2 UA awards",
    procurementMethodType=STAGE_2_UA_TYPE,
)
class CDStage2UATenderAwardResource(UATenderAwardResource):
    @json_view(
        content_type="application/json",
        permission="create_award",  # admins only
        validators=(
            validate_input_data(UAPostAward),
            validate_create_award_not_in_allowed_period,
            validate_create_award_only_for_active_lot,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(
                UAPatchAward,
                none_means_remove=True,
            ),
            validate_patch_data_simple(UAAward, item_name="award"),
            validate_award_with_lot_cancellation_in_pending,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
            validate_update_award_status_before_milestone_due_date,
        ),
    )
    def patch(self):
        return super().patch()
