from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import json_view, context_unpack, update_logging_context
from openprocurement.tender.core.procedure.utils import (
    save_tender,
    set_item,
)
from openprocurement.tender.core.procedure.serializers.award import AwardSerializer
from openprocurement.tender.core.procedure.state.award import AwardState
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_create_award_not_in_allowed_period,
    validate_create_award_only_for_active_lot,
)
from openprocurement.tender.core.procedure.models.award import PostAward
from pyramid.security import Allow, Everyone
from logging import getLogger

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

        if "awards" not in tender:
            tender["awards"] = []
        tender["awards"].append(award)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created tender award {award['id']}",
                extra=context_unpack(self.request,
                                     {"MESSAGE_ID": "tender_award_create"},
                                     {"award_id": award["id"]}),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Awards".format(tender["procurementMethodType"]),
                tender_id=tender["_id"],
                award_id=award["id"]
            )
            return {"data": self.serializer_class(award).data}

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        tender = self.request.validated["tender"]
        data = [self.serializer_class(b).data for b in tender.get("awards", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated["award"]).data
        return {"data": data}

    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            award = self.request.validated["award"]
            self.state.validate_award_patch(award, updated)

            set_item(self.request.validated["tender"], "awards", award["id"], updated)
            self.state.award_on_patch(award, updated)
            self.state.always(self.request.validated["tender"])
            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated tender award {}".format(award["id"]),
                    extra=context_unpack(self.request,
                                         {"MESSAGE_ID": "tender_award_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
