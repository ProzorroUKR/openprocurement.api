import logging
from openprocurement.api.utils import error_handler, context_unpack
from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now

logger = logging.getLogger(__name__)


class BidState(BaseState):

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        # this logic moved here from validate_update_bid_status validator
        # if request.authenticated_role != "Administrator":
        if after != "active":
            self.request.errors.add("body", "bid", "Can't update bid to ({}) status".format(after))
            self.request.errors.status = 403
            raise error_handler(self.request)

    def on_post(self, data):
        now = get_now().isoformat()
        data["date"] = now

        lot_values = data.get("lotValues")
        if lot_values:  # TODO: move to post model as serializible
            for lot_value in lot_values:
                lot_value["date"] = now
        super().on_post(data)

    def on_patch(self, before, after):
        now = get_now().isoformat()
        # if value.amount is going to be changed -> update "date"
        amount_before = (before.get("value") or {}).get("amount")
        amount_after = (after.get("value") or {}).get("amount")
        if amount_before != amount_after:
            logger.info(
                f"Bid value amount changed from {amount_before} to {amount_after}",
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "bid_amount_changed"},
                    {
                        "BID_ID": after["id"],
                    },
                ),
            )
            after["date"] = get_now().isoformat()

        # the same as above, for lots
        for after_lot in after.get("lotValues") or []:
            for before_lot in before.get("lotValues") or []:
                if before_lot["relatedLot"] == after_lot["relatedLot"]:
                    if float(before_lot["value"]["amount"]) != after_lot["value"]["amount"]:
                        logger.info(
                            f'Bid lot value amount changed from {before_lot["value"]["amount"]} to {after_lot["value"]["amount"]}',
                            extra=context_unpack(
                                get_request(),
                                {"MESSAGE_ID": "bid_amount_changed"},
                                {
                                    "BID_ID": after["id"],
                                    "LOT_ID": after_lot["relatedLot"],
                                },
                            )
                        )
                        after_lot["date"] = now
                    else:
                        # all data in save_tender applied by json_patch logic
                        # which means list items applied by position
                        # so when we change order of relatedLot in lotValues
                        # this don't affect "date" fields that stays on the same positions
                        # this causes bugs: missed date and wrong date values
                        # This else statement ensures that wherever relatedLot goes,
                        # its "date" goes with it
                        after_lot["date"] = before_lot.get("date", now)
                    break
            else:  # lotValue has been just added
                after_lot["date"] = get_now().isoformat()

        super().on_patch(before, after)
