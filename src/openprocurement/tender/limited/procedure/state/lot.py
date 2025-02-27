from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationTenderDetailsState,
)


class NegotiationLotState(LotStateMixin, NegotiationTenderDetailsState):
    def lot_on_patch(self, before: dict, after: dict) -> None:
        super().lot_on_patch(before, after)
        self.validate_update_lot_with_cancellations(after)

    def update_tender_data(self) -> None:
        pass

    def validate_update_lot_with_cancellations(self, data: dict) -> None:
        if tender_created_after(RELEASE_2020_04_19):
            return

        if [
            cancellation
            for cancellation in get_tender().get("cancellations", "")
            if cancellation.get("relatedLot") == data["id"]
        ]:
            raise_operation_error(self.request, "Can't update lot that have active cancellation")
