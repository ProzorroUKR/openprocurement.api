
from openprocurement.api.utils import get_first_revision_date, get_now, raise_operation_error
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class NegotiationLotState(LotStateMixin, NegotiationTenderState):

    def lot_on_patch(self, before: dict, after: dict) -> None:
        super(NegotiationLotState, self).on_patch(after, before)
        self.validate_update_lot_with_cancellations(after)

    def update_tender_data(self) -> None:
        pass

    def validate_update_lot_with_cancellations(self, data: dict) -> None:
        tender = get_tender()
        old_rules = get_first_revision_date(tender, default=get_now()) < RELEASE_2020_04_19

        if old_rules and [
            cancellation for cancellation in tender.get("cancellations", "") if cancellation.get("relatedLot") == data["id"]
        ]:
            raise_operation_error(self.request, "Can't update lot that have active cancellation")
