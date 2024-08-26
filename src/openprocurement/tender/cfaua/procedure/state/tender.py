from logging import getLogger

from openprocurement.api.context import get_now
from openprocurement.api.utils import context_unpack
from openprocurement.tender.cfaua.constants import CLARIFICATIONS_UNTIL_PERIOD
from openprocurement.tender.cfaua.procedure.awarding import (
    CFAUATenderStateAwardingMixing,
)
from openprocurement.tender.cfaua.procedure.models.agreement import Agreement
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.utils import calculate_tender_full_date

LOGGER = getLogger(__name__)


class CFAUATenderState(CFAUATenderStateAwardingMixing, TenderState):
    active_bid_statuses = ("active", "pending")
    block_tender_complaint_status = ("claim", "pending", "accepted", "satisfied", "stopping")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    def contract_events(self, tender):
        yield from ()  # empty , this procedure doesn't have contracts

    def qualification_stand_still_events(self, tender):
        active_lots = [lot["id"] for lot in tender.get("lots", "") if lot["status"] == "active"]
        # should be set on change status to active.qualification.stand-still
        award_period_end = tender["awardPeriod"]["endDate"]
        if not any(
            i["status"] in self.block_complaint_status
            for a in tender.get("awards", "")
            for i in a.get("complaints", "")
            if a["lotID"] in active_lots
        ):
            yield award_period_end, self.qualification_stand_still_handler

    def qualification_stand_still_handler(self, tender):
        statuses = set()
        for lot in tender.get("lots", ""):
            active_awards_count = sum(
                1 for i in tender.get("awards", "") if i["lotID"] == lot["id"] and i["status"] == "active"
            )
            if active_awards_count < tender["config"]["minBidsNumber"]:
                LOGGER.info(
                    "Switched lot {} of tender {} to {}".format(lot["id"], tender["_id"], "unsuccessful"),
                    extra=context_unpack(
                        get_request(),
                        {"MESSAGE_ID": "switched_lot_unsuccessful"},
                        {"LOT_ID": lot["id"]},
                    ),
                )
                self.set_object_status(lot, "unsuccessful")
            statuses.add(lot["status"])

        if not statuses.difference({"unsuccessful"}):
            self.get_change_tender_status_handler("unsuccessful")(tender)
        else:
            self.get_change_tender_status_handler("active.awarded")(tender)
            clarification_date = calculate_tender_full_date(
                get_now(),
                CLARIFICATIONS_UNTIL_PERIOD,
                tender=tender,
                working_days=False,
            )
            tender["contractPeriod"] = {
                "startDate": get_now().isoformat(),
                "clarificationsUntil": clarification_date.isoformat(),
            }
            self.prepare_agreements(tender)

    # utils
    @staticmethod
    def prepare_agreements(tender):
        if "agreements" not in tender:
            tender["agreements"] = []

        for lot in tender.get("lots"):
            if lot["status"] == "active":
                items = [i for i in tender.get("items", "") if i.get("relatedLot") == lot["id"]]
                unit_prices = [
                    {
                        "relatedItem": item["id"],
                        "value": {
                            "currency": tender["value"]["currency"],
                            "valueAddedTaxIncluded": tender["value"]["valueAddedTaxIncluded"],
                        },
                    }
                    for item in items
                ]

                contracts = []
                for award in tender.get("awards", ""):
                    if award["lotID"] == lot["id"] and award["status"] == "active":
                        contracts.append(
                            {
                                "suppliers": award["suppliers"],
                                "awardID": award["id"],
                                "bidID": award["bid_id"],
                                "date": get_now().isoformat(),
                                "unitPrices": unit_prices,
                                "parameters": [b for b in tender.get("bids", "") if b["id"] == award["bid_id"]][0].get(
                                    "parameters", []
                                ),
                            }
                        )
                server_id = get_request().registry.server_id
                data = {
                    "agreementID": f"{tender['tenderID']}-{server_id}{len(tender.get('agreements', '')) + 1}",
                    "date": get_now().isoformat(),
                    "contracts": contracts,
                    "items": items,
                    "features": tender.get("features", []),
                    "status": "pending",
                }
                agreement = Agreement(data)
                tender["agreements"].append(agreement.serialize())

    def invalidate_bids_data(self, tender):
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"
