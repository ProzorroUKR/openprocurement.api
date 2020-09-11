# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource, apply_patch
from openprocurement.api.utils import context_unpack, get_now, json_view
from openprocurement.tender.openeu.views.bid import TenderBidResource as BaseResourceEU
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.validation import (
    validate_patch_bid_data,
    validate_update_deleted_bid,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
    validate_bid_status_update_not_to_pending,
    validate_bid_activate_criteria,
)
from openprocurement.tender.competitivedialogue.validation import validate_bid_status_update_not_to_pending_or_draft


@json_view(
    validators=(
        validate_bid_operation_not_in_tendering,
        validate_bid_operation_period,
        validate_update_deleted_bid,
        validate_bid_status_update_not_to_pending_or_draft,
        validate_bid_activate_criteria,
    )
)
def patch_bid_first_stage(self):
    """Update of proposal

                Example request to change bid proposal:

                .. sourcecode:: http

                    PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
                    Host: example.com
                    Accept: application/json

                    {
                        "data": {
                            "value": {
                                "amount": 600
                            }
                        }
                    }

                And here is the response to be expected:

                .. sourcecode:: http

                    HTTP/1.0 200 OK
                    Content-Type: application/json

                    {
                        "data": {
                            "value": {
                                "amount": 600,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        }
                    }

                """
    self.request.validated["tender"].modified = False
    if apply_patch(self.request, src=self.request.context.serialize()):
        self.LOGGER.info(
            "Updated tender bid {}".format(self.request.context.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_patch"}),
        )
        return {"data": self.request.context.serialize("view")}


@optendersresource(
    name="{}:Tender Bids".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bids",
)
class CompetitiveDialogueEUBidResource(BaseResourceEU):
    """ Tender EU bids """

    patch = json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_patch_bid_data,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_update_deleted_bid,
            validate_bid_status_update_not_to_pending,
            validate_bid_activate_criteria,
        ),
    )(patch_bid_first_stage)


@optendersresource(
    name="{}:Tender Bids".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bids",
)
class CompetitiveDialogueUABidResource(BaseResourceEU):
    """ Tender UA bids """

    patch = json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_patch_bid_data,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_update_deleted_bid,
            validate_bid_status_update_not_to_pending,
            validate_bid_activate_criteria,
        ),
    )(patch_bid_first_stage)
