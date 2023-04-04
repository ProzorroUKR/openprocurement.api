from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.awarding import TenderStateAwardingMixing
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.context import get_now, since_2020_rules
from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.state.chronograph import ChronographEventsMixing
from openprocurement.tender.core.procedure.state.auction import BaseShouldStartAfterMixing
from logging import getLogger


LOGGER = getLogger(__name__)


class TenderState(BaseShouldStartAfterMixing, TenderStateAwardingMixing, ChronographEventsMixing, BaseState):
    min_bids_number = 2
    active_bid_statuses = ("active",)  # are you intrigued ?
    # used by bid counting methods

    block_complaint_status = ("answered", "pending")
    block_tender_complaint_status = ("claim", "pending", "accepted", "satisfied", "stopping")
    # tender can't proceed to "active.auction" until has a tender.complaints in one of statuses above
    unsuccessful_statuses = ("cancelled", "unsuccessful")
    terminated_statuses = ("complete", "unsuccessful", "cancelled", "draft.unsuccessful")

    contract_model = Contract

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        data["date"] = get_now().isoformat()

        # TODO: redesign auction planning
        if after in self.unsuccessful_statuses:
            self.remove_all_auction_periods(data)

    def always(self, data):
        super().always(data)
        self.update_next_check(data)
        self.calc_auction_periods(data)

    def on_post(self, data):
        self.validate_config(data)
        super().on_post(data)

    def validate_config(self, data):
        self._validate_has_auction(data)

    def _validate_has_auction(self, data):
        pmt = data.get("procurementMethodType")
        if pmt in ("reporting", "negotiation", "negotiation.quick"):
            if not self.config.get("hasAuction"):
                raise_operation_error(
                    self.request,
                    "Config field hasAuction must be false for procurementMethodType {}".format(pmt)
                )



    # UTILS (move to state ?)
    # belowThreshold
    @staticmethod
    def cancellation_blocks_tender(tender, lot_id=None):
        """
        A pending cancellation stop the tender process
        until the either tender is cancelled or cancellation is cancelled 🤯
        :param tender:
        :param lot_id: if passed, then other lot cancellations are not considered
        :return:
        """
        if not since_2020_rules() \
           or tender["procurementMethodType"] in ("belowThreshold", "closeFrameworkAgreementSelectionUA"):
            return False

        related_cancellations = [
            c for c in tender.get("cancellations", "")
            if lot_id is None  # we don't care of lot
            or c.get("relatedLot") in (None, lot_id)  # it's tender or this lot cancellation
        ]

        if any(
            i["status"] == "pending"
            for i in related_cancellations
        ):
            return True

        # unsuccessful also blocks tender
        accept_tender = all(
            any(complaint["status"] == "resolved" for complaint in c.get("complaints"))
            for c in related_cancellations
            if c["status"] == "unsuccessful" and c.get("complaints")
        )
        return not accept_tender

    def validate_cancellation_blocks(self, request, tender, lot_id=None):
        if self.cancellation_blocks_tender(tender, lot_id):
            raise_operation_error(request, "Can't perform action due to a pending cancellation")
