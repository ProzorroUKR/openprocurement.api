from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.lot import Lot, PatchLot, PostLot
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsState,
    TenderLotRulesMixin,
)


class LotStateMixin(TenderLotRulesMixin):
    """
    lots endpoint: request validation and hooks

    The lot rules themselves (TenderLotRulesMixin) are shared with the tender endpoint: the hooks apply
    the lot change to the tender and run the tender on_patch, so both endpoints validate lots identically.
    """

    post_data_model = PostLot
    patch_data_model = PatchLot
    data_model = Lot

    # items get their relatedLot through the tender endpoint, in a separate request
    related_lot_in_items_check = False
    items_related_lot_check = False

    def validate_lot_post_request(self):
        self.validate_lot_request_allowed()
        lot = self.validate_input_data(self.get_post_data_model())
        self.validate_lot_value(get_tender(), lot)

    def validate_lot_patch_request(self):
        self.validate_lot_request_allowed()
        self.validate_patch_input_data(self.get_patch_data_model())
        if lot := self.validate_patch_data_simple(self.get_data_model(), "lot"):
            # the lot is validated as submitted, before the value / minimalStep meta is taken from the tender:
            # currency and valueAddedTaxIncluded of the lot value and minimalStep must match.
            # Via the tender endpoint the meta is applied first (clients rely on that inheritance).
            self.validate_lot_value(get_tender(), lot)

    def validate_lot_delete_request(self):
        self.validate_lot_request_allowed()

    def validate_lot_request_allowed(self):
        if self.request.authenticated_role != "Administrator":
            self.validate_item_owner("tender")
        self.validate_lot_operation_allowed(get_tender())

    def lot_on_post(self, lot: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def lot_on_patch(self, before: dict, after: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def lot_on_delete(self, lot: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())


class LotState(LotStateMixin, TenderDetailsState):
    pass
