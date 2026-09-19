from typing import Callable

from openprocurement.api.constants_env import CRITERION_REQUIREMENT_STATUSES_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsState,
)
from openprocurement.tender.core.procedure.utils import tender_created_before
from openprocurement.tender.core.procedure.validation import OPERATIONS


class LotStateMixin:
    request: Callable

    get_lot_auction_should_start_after: Callable
    set_lot_minimal_step: Callable
    set_lot_value: Callable
    set_lot_guarantee: Callable
    calc_tender_values: Callable
    invalidate_review_requests: Callable
    validate_action_with_exist_inspector_review_request: Callable
    validate_cancellation_blocks: Callable
    validate_tender_period_extension: Callable
    validate_lot_value: Callable
    validate_lot_minimal_step: Callable

    should_validate_lot_minimal_step = True
    # limited (negotiation): lots don't recalculate the tender values
    lot_updates_tender_values = True
    # cfaua: limits of the lots count (None = no limit)
    lots_min_count: int | None = None
    lots_max_count: int | None = None
    # limited (negotiation): lots can't be added/updated/deleted when the tender has awards
    lot_operations_forbidden_with_awards = False

    def validate_lot_post(self, lot) -> None:
        request, tender = get_request(), get_tender()
        self.validate_lots_max_count(tender)
        self.validate_lot_operation_with_awards(tender)
        self.validate_tender_period_extension(tender)
        self.validate_cancellation_blocks(request, tender)

    def lot_on_post(self, data: dict) -> None:
        tender = get_tender()
        self.pre_save_validations(data)
        self.validate_lot_minimal_step(data)
        self.validate_lot_value(tender, data)
        self.set_lot_data(data)
        self.lot_always(data)

    def validate_lot_patch(self, before: dict, after: dict) -> None:
        request, tender = get_request(), get_tender()
        self.validate_lot_operation_with_awards(tender)
        self.validate_tender_period_extension(tender)
        self.validate_cancellation_blocks(request, tender, lot_id=before["id"])

    def lot_on_patch(self, before: dict, after: dict) -> None:
        tender = get_tender()
        self.pre_save_validations(after)
        self.validate_lot_minimal_step(after, before=before)
        self.validate_lot_value(tender, after)
        self.set_lot_data(after)
        self.lot_always(after)
        if "status" in after and before["status"] != after["status"]:
            self.lot_status_up(before["status"], after["status"], after)

    def validate_lot_delete(self, lot) -> None:
        request, tender = get_request(), get_tender()
        self.validate_lot_delete_related_objects(tender, lot)
        self.validate_lots_min_count(tender)
        self.validate_lot_operation_with_awards(tender)
        self.validate_tender_period_extension(tender)
        self.validate_cancellation_blocks(request, tender, lot_id=lot["id"])

    def validate_lot_delete_related_objects(self, tender, lot) -> None:
        lot_id = lot["id"]
        if not tender_created_before(CRITERION_REQUIREMENT_STATUSES_FROM):
            has_active_requirements = any(
                criterion.get("relatedItem", "") == lot_id and requirement["status"] == "active"
                for criterion in tender.get("criteria", "")
                for rg in criterion.get("requirementGroups", "")
                for requirement in rg.get("requirements", "")
            )
            if has_active_requirements:
                raise_operation_error(
                    get_request(),
                    f"Can't delete {lot_id} lot while related criterion has active requirements",
                )
        for collection_name in ("cancellations", "milestones", "items"):
            if any(i.get("relatedLot", "") == lot_id for i in tender.get(collection_name, "")):
                raise_operation_error(get_request(), f"Cannot delete lot with related {collection_name}", status=422)

    def validate_lots_min_count(self, tender) -> None:
        if self.lots_min_count is not None and len(tender.get("lots", "")) <= self.lots_min_count:
            raise_operation_error(
                get_request(), f"Lots count in tender cannot be less than {self.lots_min_count} items"
            )

    def validate_lots_max_count(self, tender) -> None:
        if self.lots_max_count is not None and len(tender.get("lots", "")) >= self.lots_max_count:
            raise_operation_error(
                get_request(), f"Lots count in tender cannot be more than {self.lots_max_count} items"
            )

    def validate_lot_operation_with_awards(self, tender) -> None:
        if self.lot_operations_forbidden_with_awards and tender.get("awards"):
            request = get_request()
            raise_operation_error(request, f"Can't {OPERATIONS.get(request.method)} lot when you have awards")

    def lot_on_delete(self, data: dict) -> None:
        self.lot_always(data)

    def lot_status_up(self, status_before, status_after, data):
        if status_before != "active":
            self.request.errors.add("body", "lot", "Can't update lot to ({}) status".format(status_after))
            self.request.errors.status = 403
            raise error_handler(self.request)

    def lot_always(self, data: dict) -> None:
        self.validate_action_with_exist_inspector_review_request()
        self.invalidate_review_requests()
        self.update_tender_data()

    def pre_save_validations(self, data: dict) -> None:
        self.validate_lots_unique()

    def update_tender_data(self) -> None:
        if not self.lot_updates_tender_values:
            return
        tender = get_tender()
        self.calc_tender_values(tender)

    def set_lot_data(self, data: dict) -> None:
        tender = get_tender()
        self.set_auction_period_should_start_after(tender, data)
        self.set_lot_guarantee(tender, data)
        self.set_lot_value(tender, data)
        self.set_lot_minimal_step(tender, data)

    def set_auction_period_should_start_after(self, tender: dict, data: dict) -> None:
        if tender["config"]["hasAuction"] is False:
            return

        should_start_after = self.get_lot_auction_should_start_after(tender, data)
        if not should_start_after:
            return
        auction_period = data.get("auctionPeriod") or {}
        auction_period["shouldStartAfter"] = should_start_after
        data["auctionPeriod"] = auction_period
        # if auctionPeriod was calculated in draft tender before lots were added
        if tender.get("auctionPeriod"):
            del tender["auctionPeriod"]

    def validate_lots_unique(self) -> None:
        tender = get_tender()

        if tender.get("lots"):
            ids = [i["id"] for i in tender["lots"]]
            if [i for i in set(ids) if ids.count(i) > 1]:
                raise_operation_error(
                    self.request,
                    "Items should be unique by fields: id",
                    status=422,
                    name="lots",
                )


class LotInvalidationBidStateMixin(LotStateMixin):
    def lot_always(self, data: dict) -> None:
        super().lot_always(data)
        self.invalidate_lot_bids_data()

    def invalidate_lot_bids_data(self):
        self.invalidate_bids_data(get_tender())


class LotState(LotStateMixin, TenderDetailsState):
    pass
