from pyramid.request import Request

from openprocurement.api.utils import raise_operation_error, error_handler
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import (
    get_tender,
    get_request,
    get_tender_config,
)


class LotStateMixin:
    request: Request
    calc_tender_values: callable
    get_lot_auction_should_start_after: callable
    validate_cancellation_blocks: callable  # from TenderState
    validate_minimal_step: callable  # from TenderState

    def validate_lot_post(self, lot) -> None:
        request, tender = get_request(), get_tender()
        self.validate_cancellation_blocks(request, tender)

    def lot_on_post(self, data: dict) -> None:
        self.pre_save_validations(data)
        self.validate_minimal_step(data)
        self.set_lot_data(data)
        self.lot_always(data)

    def validate_lot_patch(self, before: dict, after: dict) -> None:
        request, tender = get_request(), get_tender()
        self.validate_cancellation_blocks(request, tender, lot_id=before["id"])

    def lot_on_patch(self, before: dict, after: dict) -> None:
        self.pre_save_validations(after)
        self.validate_minimal_step(after, before=before)
        self.set_lot_data(after)
        self.lot_always(after)
        if "status" in after and before["status"] != after["status"]:
            self.lot_status_up(before["status"], after["status"], after)

    def validate_lot_delete(self, lot) -> None:
        request, tender = get_request(), get_tender()
        self.validate_cancellation_blocks(request, tender, lot_id=lot["id"])

    def lot_on_delete(self, data: dict) -> None:
        self.lot_always(data)

    def lot_status_up(self, status_before, status_after, data):
        if status_before != "active":
            self.request.errors.add("body", "lot", "Can't update lot to ({}) status".format(status_after))
            self.request.errors.status = 403
            raise error_handler(self.request)

    def lot_always(self, data: dict) -> None:
        self.update_tender_data()

    def pre_save_validations(self, data: dict) -> None:
        self.validate_lots_unique()

    def update_tender_data(self) -> None:
        tender = get_tender()
        self.calc_tender_values(tender)

    def set_lot_data(self, data: dict) -> None:
        tender = get_tender()
        self.set_auction_period_should_start_after(tender, data)

    def set_auction_period_should_start_after(self, tender: dict, data: dict) -> None:
        should_start_after = self.get_lot_auction_should_start_after(tender, data)
        if not should_start_after:
            return
        auction_period = data.get("auctionPeriod") or {}
        auction_period["shouldStartAfter"] = should_start_after
        data["auctionPeriod"] = auction_period

    def validate_lots_unique(self) -> None:
        tender = get_tender()

        if tender.get("lots"):
            ids = [i["id"] for i in tender["lots"]]
            if [i for i in set(ids) if ids.count(i) > 1]:
                raise_operation_error(
                    self.request,
                    "Lot id should be uniq for all lots",
                    status=422,
                    name="lots",
                )


class LotInvalidationBidStateMixin(LotStateMixin):

    tender_details_state_class: object
    invalidate_bids_data: callable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tender_details_state = self.tender_details_state_class(self.request)

    def lot_always(self, data: dict) -> None:
        super().lot_always(data)
        self.invalidate_lot_bids_data()

    def invalidate_lot_bids_data(self):
        tender = get_tender()
        self.tender_details_state.invalidate_bids_data(tender)


class LotState(LotStateMixin, TenderState):
    pass
