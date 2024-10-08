from logging import getLogger
from typing import List, Optional, Tuple

from pyramid.request import Request
from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import (
    context_unpack,
    get_now,
    json_view,
    update_logging_context,
)
from openprocurement.tender.core.procedure.models.lot import Lot, PatchLot, PostLot
from openprocurement.tender.core.procedure.serializers.lot import LotSerializer
from openprocurement.tender.core.procedure.state.lot import LotState
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    validate_delete_lot_related_object,
    validate_lot_operation_in_disallowed_tender_statuses,
    validate_operation_with_lot_cancellation_in_pending,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate

LOGGER = getLogger(__name__)


def resolve_lot(request: Request) -> None:
    match_dict = request.matchdict
    if match_dict.get("lot_id"):
        lot_id = match_dict["lot_id"]
        lot = get_items(request, request.validated["tender"], "lots", lot_id)
        request.validated["lot"] = lot[0]


class TenderLotResource(TenderBaseResource):
    state_class = LotState
    serializer_class = LotSerializer

    def __acl__(self) -> List[Tuple[str, str, str]]:
        return [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_lot"),
            (Allow, "g:Administrator", "create_lot"),
            (Allow, "g:brokers", "edit_lot"),
            (Allow, "g:Administrator", "edit_lot"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]

    def __init__(self, request: Request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_lot(request)

    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(PostLot),
        ),
    )
    def collection_post(self) -> Optional[dict]:
        """
        Lot creation
        """

        update_logging_context(self.request, {"lot_id": "__new__"})

        tender = self.request.validated["tender"]
        lot = self.request.validated["data"]
        lot["date"] = get_now().isoformat()
        self.state.validate_lot_post(lot)

        if "lots" not in tender:
            tender["lots"] = []
        tender["lots"].append(lot)

        self.state.lot_on_post(lot)
        self.state.always(self.request.validated["tender"])

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created tender lot {lot['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_lot_create"},
                    {"award_id": lot["id"]},
                ),
            )
            self.request.response.status = 201
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Lots".format(route_prefix),
                tender_id=tender["_id"],
                lot_id=lot["id"],
            )
            return {"data": self.serializer_class(lot).data}

    @json_view(
        permission="view_tender",
    )
    def collection_get(self) -> dict:
        """
        Get all tender lots
        """

        tender = self.request.validated["tender"]
        data = [self.serializer_class(b).data for b in tender.get("lots", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self) -> dict:
        """
        Get lot information by id
        """
        data = self.serializer_class(self.request.validated["lot"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(PatchLot),
            validate_patch_data_simple(Lot, item_name="lot"),
            validate_operation_with_lot_cancellation_in_pending("lot"),
        ),
        permission="edit_lot",
    )
    def patch(self) -> Optional[dict]:
        """
        Lot updating
        """

        updated = self.request.validated["data"]
        if not updated:
            return

        lot = self.request.validated["lot"]
        self.state.validate_lot_patch(lot, updated)

        set_item(self.request.validated["tender"], "lots", lot["id"], updated)

        self.state.lot_on_patch(lot, updated)
        self.state.always(self.request.validated["tender"])

        if save_tender(self.request):
            self.LOGGER.info(
                f"Updated tender lot {lot['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_patch"}),
            )
            return {"data": self.serializer_class(updated).data}

    @json_view(
        permission="edit_lot",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_operation_with_lot_cancellation_in_pending("lot"),
            validate_delete_lot_related_object,
        ),
    )
    def delete(self) -> Optional[dict]:
        """
        Lot deleting
        """

        lot = self.request.validated["lot"]
        tender = self.request.validated["tender"]

        self.state.validate_lot_delete(lot)

        tender["lots"].remove(lot)
        if not tender["lots"]:
            del tender["lots"]
        self.state.lot_on_delete(lot)
        self.state.always(self.request.validated["tender"])

        if save_tender(self.request):
            self.LOGGER.info(
                f"Deleted tender lot {lot['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_delete"}),
            )
            return {"data": self.serializer_class(lot).data}
