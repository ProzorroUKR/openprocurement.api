from logging import getLogger
from openprocurement.tender.core.utils import context_unpack
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.tender.core.procedure.utils import tender_created_in
from openprocurement.tender.core.procedure.awarding import TenderStateAwardingMixing
from openprocurement.tender.openuadefense.procedure.settings import BLOCK_COMPLAINT_STATUSES
from openprocurement.api.constants import NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO

LOGGER = getLogger("openprocurement.tender.openuadefense")


class DefenseTenderStateAwardingMixing(TenderStateAwardingMixing):

    def add_next_award(self):
        super().add_next_award()
        self.process_new_defense_complaints()

    def process_new_defense_complaints(self):
        if not tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO):
            return

        tender = get_tender()
        lots = tender.get("lots")
        if lots:
            statuses = set()
            for lot in lots:
                if lot["status"] == "active":
                    lot_awards = [i for i in tender.get("awards", "") if i["lotID"] == lot["id"]]
                    statuses.add(lot_awards[-1]["status"] if lot_awards else "unsuccessful")

            if statuses == {"unsuccessful"}:
                for lot in lots:
                    if lot["status"] == "active":
                        lot_awards = [i for i in tender.get("awards", "") if i["lotID"] == lot["id"]]
                        if not lot_awards:
                            continue

                        pending_complaints = any(
                            i["status"] in BLOCK_COMPLAINT_STATUSES
                            and i.get("relatedLot") == lot["id"]
                            for i in tender.get("complaints", "")
                        )
                        awards_no_complaint_periods = all(
                            not a.get("complaintPeriod")
                            for a in lot_awards
                            if a["status"] == "unsuccessful"
                        )
                        if (
                            not pending_complaints
                            and awards_no_complaint_periods
                        ):
                            LOGGER.info(
                                "Switched lot {} of tender {} to {}".format(lot["id"], tender["_id"], "unsuccessful"),
                                extra=context_unpack(
                                    get_request(),
                                    {"MESSAGE_ID": "switched_lot_unsuccessful"},
                                    {"LOT_ID": lot["id"]}
                                ),
                            )
                            self.set_object_status(lot, "unsuccessful")

                lot_statuses = {lot["status"] for lot in lots}
                if not lot_statuses.difference({"unsuccessful", "cancelled"}):
                    self.get_change_tender_status_handler("unsuccessful")(tender)

        else:
            if (
                tender["awards"][-1]["status"] == "unsuccessful" and
                all(i["status"] not in BLOCK_COMPLAINT_STATUSES
                    for i in tender.get("complaints", "")) and
                all(
                    not a.get("complaintPeriod")
                    for a in tender.get("awards", "")
                    if a["status"] == "unsuccessful"
                )
            ):
                self.get_change_tender_status_handler("unsuccessful")(tender)
