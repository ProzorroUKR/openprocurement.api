from openprocurement.tender.cfaua.procedure.models.award import Award
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now


class CFAUATenderStateAwardingMixing:
    set_object_status: callable
    awarding_criteria_key: str = "amount"
    reverse_awarding_criteria: bool = False

    def add_next_award(self, regenerate_all_awards=False, lot_id=None):
        request = get_request()
        tender = request.validated["tender"]
        if not tender.get("awardPeriod"):
            tender["awardPeriod"] = {}
        if not tender["awardPeriod"].get("startDate"):
            tender["awardPeriod"]["startDate"] = get_now().isoformat()

        statuses = set()
        for lot in tender.get("lots", ""):
            if lot["status"] == "active":
                lot_awards = [award for award in tender.get("awards", "") if award["lotID"] == lot["id"]]
                lot_awards_statuses = {award["status"] for award in lot_awards}
                if lot_awards_statuses and lot_awards_statuses.issubset({"pending", "active"}):
                    statuses.union(lot_awards_statuses)  # this line does nothing as .union( doesn't work "inplace"! Fix?
                    continue

                all_bids = self.prepare_bids_for_awarding(tender, tender["bids"], lot_id=lot["id"])
                if not all_bids:
                    self.set_object_status(lot, "unsuccessful")
                    statuses.add("unsuccessful")
                    continue

                selected_bids = self.exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=lot["id"])

                if not regenerate_all_awards and lot["id"] == lot_id:
                    # this block seems is supposed to cause the function append only one award
                    # for a bid of the first (the only?) cancelled award
                    cancelled_award_bid_ids = [
                        award["bid_id"] for award in lot_awards
                        if award["status"] == "cancelled"
                        and "award" in request.validated
                        and request.validated["award"]["id"] == award["id"]
                    ]
                    if cancelled_award_bid_ids:
                        selected_bids = [bid for bid in all_bids if bid["id"] == cancelled_award_bid_ids[0]]

                if tender.get("maxAwardsCount"):  # limit awards
                    selected_bids = selected_bids[:tender["maxAwardsCount"]]

                active_award_bid_ids = {a["bid_id"] for a in lot_awards if a["status"] in ("active", "pending")}
                selected_bids = list([b for b in selected_bids if b["id"] not in active_award_bid_ids])
                if selected_bids:
                    for bid in selected_bids:
                        self.tender_append_award(tender, Award, bid, all_bids, lot_id=lot["id"])
                    statuses.add("pending")
                else:
                    statuses.add("unsuccessful")
        if (
            statuses.difference({"unsuccessful", "active"})
            and any(i for i in tender.get("lots"))   # wtf is this check ??
        ):
            # logic for auction to switch status
            if "endDate" in tender["awardPeriod"]:
                del tender["awardPeriod"]["endDate"]
            self.set_object_status(tender, "active.qualification")
