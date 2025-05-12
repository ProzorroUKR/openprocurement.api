from logging import getLogger

from pyramid.security import Allow, Everyone

from openprocurement.api.database import atomic_transaction
from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.tender.core.procedure.contracting import (
    save_contracts_to_contracting,
    update_econtracts_statuses,
)
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.models.award import PostAward
from openprocurement.tender.core.procedure.serializers.award import AwardSerializer
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.state.award import AwardState
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    validate_create_award_not_in_allowed_period,
    validate_create_award_only_for_active_lot,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.utils import (
    ProcurementMethodTypePredicate,
    context_view,
)

LOGGER = getLogger(__name__)


def resolve_award(request):
    match_dict = request.matchdict
    if match_dict.get("award_id"):
        awards = get_items(request, request.validated["tender"], "awards", match_dict["award_id"])
        request.validated["award"] = awards[0]
        # used by item validator in pq award patch endpoint
        if "bid_id" in awards[0]:  # reporting
            bids = get_items(request, request.validated["tender"], "bids", awards[0]["bid_id"])
            request.validated["bid"] = bids[0]


class TenderAwardResource(TenderBaseResource):
    serializer_class = AwardSerializer
    state_class = AwardState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "edit_award"),
            (Allow, "g:admins", "create_award"),
            (Allow, "g:admins", "edit_award"),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_award(request)

    @json_view(
        content_type="application/json",
        permission="create_award",  # admins only
        validators=(
            validate_input_data(PostAward),
            validate_create_award_not_in_allowed_period,
            validate_create_award_only_for_active_lot,
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"award_id": "__new__"})

        tender = self.request.validated["tender"]
        award = self.request.validated["data"]
        self.state.award_on_post(award)

        if "awards" not in tender:
            tender["awards"] = []
        tender["awards"].append(award)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created tender award {award['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_award_create"},
                    {"award_id": award["id"]},
                ),
            )
            self.request.response.status = 201
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Awards".format(route_prefix),
                tender_id=tender["_id"],
                award_id=award["id"],
            )
            return {"data": self.serializer_class(award, tender=tender).data}

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        tender = self.request.validated["tender"]
        data = [self.serializer_class(b, tender=tender).data for b in tender.get("awards", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": (TenderBaseSerializer, TENDER_MASK_MAPPING),
        }
    )
    def get(self):
        award = self.request.validated["award"]
        tender = self.request.validated["tender"]
        data = self.serializer_class(award, tender=tender).data
        return {"data": data}

    def patch(self):
        updated = self.request.validated["data"]
        tender = self.request.validated["tender"]
        if updated:
            award = self.request.validated["award"]
            self.state.validate_award_patch(award, updated)

            set_item(tender, "awards", award["id"], updated)
            self.state.award_on_patch(award, updated)
            self.state.always(self.request.validated["tender"])
            with atomic_transaction():
                if save_tender(self.request):
                    if contracts_added := self.request.validated.get("contracts_added"):
                        save_contracts_to_contracting(contracts_added, award)

                    if contracts_cancelled := self.request.validated.get("contracts_cancelled"):
                        update_econtracts_statuses(contracts_cancelled, "cancelled")

                    self.LOGGER.info(
                        "Updated tender award {}".format(award["id"]),
                        extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_patch"}),
                    )
                    return {"data": self.serializer_class(updated, tender=tender).data}
