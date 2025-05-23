from logging import getLogger

from cornice.resource import resource

from openprocurement.api.auth import ACCR_2
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_accreditation_level,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.belowthreshold.procedure.views.bid import (
    BelowThresholdTenderBidResource,
)
from openprocurement.tender.core.procedure.models.bid import (
    filter_administrator_bid_update,
)
from openprocurement.tender.core.procedure.validation import (
    validate_bid_operation_not_in_tendering,
    validate_bid_operation_period,
    validate_update_deleted_bid,
)
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.models.bid import (
    Bid,
    PatchBid,
    PostBid,
)
from openprocurement.tender.pricequotation.procedure.state.bid import (
    CataloguePQBidState,
    PQBidState,
)

LOGGER = getLogger(__name__)


@resource(
    name=f"{PQ}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=PQ,
    description="Tender bids",
)
class PQTenderBidResource(BelowThresholdTenderBidResource):
    state_class = PQBidState

    state_classes = {
        ELECTRONIC_CATALOGUE_TYPE: CataloguePQBidState,
        DPS_TYPE: PQBidState,
    }

    def __init__(self, request, context=None):
        self.states = {}
        for agreement_type, state_class in self.state_classes.items():
            self.states[agreement_type] = state_class(request)
        super().__init__(request, context)

    @property
    def state(self):
        agreement = get_object("agreement") or {}
        return self.states.get(agreement.get("agreementType"), self.states["default"])

    @state.setter
    def state(self, value):
        self.states["default"] = value

    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_accreditation_level(
                levels=(ACCR_2,),
                item="bid",
                operation="creation",
            ),
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_input_data(PostBid),
            validate_data_documents(route_key="bid_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            unless_administrator(validate_item_owner("bid")),
            validate_update_deleted_bid,
            validate_input_data(
                PatchBid,
                filters=(filter_administrator_bid_update,),
                none_means_remove=True,
            ),
            validate_patch_data_simple(Bid, item_name="bid"),
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
        ),
    )
    def patch(self):
        return super().patch()

    @json_view(
        permission="edit_bid",
        validators=(
            validate_item_owner("bid"),
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
        ),
    )
    def delete(self):
        return super().delete()
