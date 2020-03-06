# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.cancellation import BaseTenderCancellationResource
from openprocurement.tender.openua.validation import validate_not_only_unsuccessful_awards_or_qualifications
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_cancellation_data,
    validate_patch_cancellation_data,
    validate_cancellation_of_active_lot,
    validate_cancellation_statuses,
    validate_create_cancellation_in_active_auction,
    validate_edit_permission,
)
from openprocurement.tender.openua.utils import add_next_award


@optendersresource(
    name="aboveThresholdUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender cancellations",
)
class TenderUaCancellationResource(BaseTenderCancellationResource):

    @staticmethod
    def add_next_award_method(request):
        configurator = request.content_configurator
        add_next_award(
            request,
            reverse=configurator.reverse_awarding_criteria,
            awarding_criteria_key=configurator.awarding_criteria_key,
        )

    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_cancellation_data,
            validate_create_cancellation_in_active_auction,
            validate_cancellation_of_active_lot,
            # from core above ^
            validate_not_only_unsuccessful_awards_or_qualifications,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderUaCancellationResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_edit_permission,
            validate_tender_not_in_terminated_status,
            validate_patch_cancellation_data,
            validate_cancellation_statuses,
            validate_cancellation_of_active_lot,
            # from core above ^,
            validate_not_only_unsuccessful_awards_or_qualifications
        ),
        permission="edit_cancellation"
    )
    def patch(self):
        return super(TenderUaCancellationResource, self).patch()
