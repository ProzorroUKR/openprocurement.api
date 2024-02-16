from logging import getLogger

from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import unless_item_owner
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.core.procedure.utils import save_tender, set_ownership
from openprocurement.tender.core.procedure.validation import validate_view_bids
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate

LOGGER = getLogger(__name__)


def resolve_bid(request):
    match_dict = request.matchdict
    if match_dict.get("bid_id"):
        bid_id = match_dict["bid_id"]
        bids = get_items(request, request.validated["tender"], "bids", bid_id)
        request.validated["bid"] = bids[0]


class TenderBidResource(TenderBaseResource):
    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_bid"),
            (Allow, "g:brokers", "edit_bid"),
            (Allow, "g:Administrator", "edit_bid"),  # wtf ???
            (Allow, "g:admins", ALL_PERMISSIONS),  # some tests use this, idk why
        ]
        return acl

    serializer_class = BidSerializer
    state_class = BidState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_bid(request)

    def collection_post(self):
        update_logging_context(self.request, {"bid_id": "__new__"})

        tender = self.request.validated["tender"]
        bid = self.request.validated["data"]
        access = set_ownership(bid, self.request)

        if "bids" not in tender:
            tender["bids"] = []
        tender["bids"].append(bid)
        # tender["numberOfBids"] = len(tender["bids"])

        self.state.on_post(bid)

        if save_tender(self.request, modified=False):
            LOGGER.info(
                "Created tender bid {}".format(bid["id"]),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_create"}, {"bid_id": bid["id"]}),
            )
            self.request.response.status = 201
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Bids".format(route_prefix),
                tender_id=tender["_id"],
                bid_id=bid["id"],
            )
            return {"data": self.serializer_class(bid).data, "access": access}

    @json_view(
        permission="view_tender",
        validators=(validate_view_bids,),
    )
    def collection_get(self):
        tender = self.request.validated["tender"]
        # data = [i.serialize(self.request.validated["tender_status"]) for i in tender.bids]
        data = tuple(self.serializer_class(b).data for b in tender.get("bids", ""))
        return {"data": data}

    @json_view(
        permission="view_tender",
        validators=(
            unless_item_owner(
                validate_view_bids,
                item_name="bid",
            ),
        ),
    )
    def get(self):
        # data depends on tender status
        # data = self.request.context.serialize(self.request.validated["tender_status"])
        data = self.serializer_class(self.request.validated["bid"]).data
        return {"data": data}

    def patch(self):
        updated_bid = self.request.validated["data"]
        if updated_bid:
            bid = self.request.validated["bid"]
            self.state.on_patch(bid, updated_bid)
            set_item(self.request.validated["tender"], "bids", bid["id"], updated_bid)
            if save_tender(self.request, modified=False):
                self.LOGGER.info(
                    f"Updated tender bid {bid['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_patch"}),
                )
                return {"data": self.serializer_class(updated_bid).data}

    def delete(self):
        bid = self.request.validated["bid"]
        tender = self.request.validated["tender"]

        tender["bids"].remove(bid)
        if not tender["bids"]:
            del tender["bids"]

        if save_tender(self.request, modified=False):
            self.LOGGER.info(
                "Deleted tender bid {}".format(bid["id"]),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_delete"}),
            )
            return {"data": self.serializer_class(bid).data}
