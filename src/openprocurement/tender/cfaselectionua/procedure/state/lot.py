from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import CFASelectionTenderDetailsState
from openprocurement.tender.core.procedure.utils import validate_field


class TenderLotState(LotStateMixin, CFASelectionTenderDetailsState):
    def validate_minimal_step(self, data, before=None):
        """
        Override to skip minimalStep required validation.
        It's required for cfaselectionua in lot level

        :param data: tender or lot
        :param before: tender or lot
        :return:
        """
        tender = get_tender()
        kwargs = {
            "before": before,
            "enabled": tender["config"]["hasAuction"] is True,
        }
        validate_field(data, "minimalStep", **kwargs)
