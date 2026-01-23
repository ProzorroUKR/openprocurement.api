from datetime import timedelta
from decimal import Decimal
from logging import getLogger
from typing import Optional

from barbecue import calculate_coeficient

from openprocurement.api.constants import CRITERION_LIFE_CYCLE_COST_IDS
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.constants import ALP_MILESTONE_REASONS
from openprocurement.tender.core.procedure.context import (
    get_bids_before_auction_results_context,
    get_request,
)
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.utils import (
    activate_bids,
    filter_features,
    get_lot_value_status,
    tender_created_after_2020_rules,
)
from openprocurement.tender.core.utils import (
    ProcurementMethodTypePredicate,
    calculate_tender_full_date,
)
from openprocurement.tender.pricequotation.constants import PQ

LOGGER = getLogger(__name__)


class TenderStateAwardingMixing:
    award_class = Award

    # Bids are sorted by this key on awarding stage
    # Most procedures use "amount" key
    # esco procedure uses "amountPerformance" key
    awarding_criteria_key: str = "amount"

    # Default configuration for awarding is reversed (from lower to higher)
    # When False, awards are generated from lower to higher by awarding_criteria_key
    # When True, awards are generated from higher to lower by awarding_criteria_key
    # esco procedure uses True
    reverse_awarding_criteria: bool = False

    # Generate award milestones
    generate_award_milestones: bool = True

    award_period_duration: int = 5

    def on_auction_results(self, tender, lot_id=None):
        if lot_id:
            for lot in tender["lots"]:
                if lot["id"] == lot_id:
                    self.finalize_auction_period(lot)
                    break

            if all(
                i.get("auctionPeriod") and i["auctionPeriod"].get("endDate")
                for i in tender["lots"]
                if i["status"] == "active"
                # I believe, bids number check only required for belowThreshold procedure
                # openua, for example, changes its lot.status to "unsuccessful"
                and self.count_lot_bids_number(tender, i["id"]) > 1
            ):
                self.add_next_award()
        else:
            self.finalize_auction_period(tender)
            self.add_next_award()

    def finalize_auction_period(self, obj):
        now = get_request_now().isoformat()

        if obj["auctionPeriod"].get("startDate", now) > now:
            obj["auctionPeriod"]["startDate"] = now

        obj["auctionPeriod"]["endDate"] = now

    def add_next_award(self):
        tender = get_tender()

        tender["awardPeriod"] = award_period = tender.get("awardPeriod", {})
        if "startDate" not in award_period:
            award_period["startDate"] = get_request_now().isoformat()

        if tender["config"]["hasAwardingOrder"] is False:
            self.generate_awards_without_awarding_order(tender)
            return

        lots = tender.get("lots")
        if lots:
            statuses = set()
            for lot in lots:
                if lot["status"] != "active":
                    continue

                lot_awards = tuple(a for a in tender.get("awards", "") if a["lotID"] == lot["id"])
                if lot_awards and lot_awards[-1]["status"] in ["pending", "active"]:
                    statuses.add(lot_awards[-1]["status"])
                    continue

                all_bids = self.prepare_bids_for_awarding(tender, tender.get("bids", []), lot_id=lot["id"])

                if all_bids:
                    bids = self.exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=lot["id"])
                    if bids:
                        self.tender_append_award(tender, bids[0], all_bids, lot_id=lot["id"])
                        request = get_request()
                        route_prefix = ProcurementMethodTypePredicate.route_prefix(request)
                        request.response.headers["Location"] = request.route_url(
                            "{}:Tender Awards".format(route_prefix),
                            tender_id=tender["_id"],
                            award_id=tender["awards"][-1]["id"],
                        )
                        statuses.add("pending")
                    else:
                        statuses.add("unsuccessful")
                else:
                    self.set_object_status(lot, "unsuccessful")
                    statuses.add("unsuccessful")

            self.recalculate_period_and_change_tender_status(
                tender,
                stays_at_qualification=statuses.difference({"unsuccessful", "active"}),
            )
        else:
            awards = tender.get("awards", [])
            if not awards or awards[-1]["status"] not in ("pending", "active"):
                all_bids = self.prepare_bids_for_awarding(tender, tender.get("bids", []), lot_id=None)
                bids = self.exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=None)
                if bids:
                    self.tender_append_award(tender, bids[0], all_bids)
                    request = get_request()
                    route_prefix = ProcurementMethodTypePredicate.route_prefix(request)
                    request.response.headers["Location"] = request.route_url(
                        "{}:Tender Awards".format(route_prefix),
                        tender_id=tender["_id"],
                        award_id=tender["awards"][-1]["id"],
                    )
                elif tender.get("procurementMethodType") == PQ:
                    self.get_change_tender_status_handler("unsuccessful")(tender)
                    return
            self.recalculate_period_and_change_tender_status(
                tender,
                stays_at_qualification=tender["awards"][-1]["status"] == "pending",
            )

    def generate_awards_without_awarding_order(self, tender):
        """
        If hasAwardingOrder set to False there is another logic in generating awards.
        If tender doesn't have awards yet and auction is sending the results,
        than all awards are generating all together.
        If tender has got awards already and award status is changing to 'cancelled',
        than new award should be generated in status 'pending' instead of cancelled award.
        """
        lots = tender.get("lots")
        if lots:
            stays_at_qualification = False
            for lot in lots:
                if lot["status"] != "active":
                    continue
                lot_awards = tuple(a for a in tender.get("awards", []) if a["lotID"] == lot["id"])
                awards_statuses = {award["status"] for award in lot_awards}
                all_bids = self.prepare_bids_for_awarding(tender, tender.get("bids", []), lot_id=lot["id"])
                if all_bids:
                    bids = self.filter_bids_for_creating_new_awards(lot_awards, all_bids)
                    if bids:
                        for bid in bids:
                            self.tender_append_award(tender, bid, all_bids, lot_id=lot["id"])
                        request = get_request()
                        route_prefix = ProcurementMethodTypePredicate.route_prefix(request)
                        request.response.headers["Location"] = request.route_url(
                            "{}:Tender Awards".format(route_prefix),
                            tender_id=tender["_id"],
                            award_id=tender["awards"][-1]["id"],
                        )
                        awards_statuses.add("pending")
                else:
                    self.set_object_status(lot, "unsuccessful")

                if awards_statuses.difference({"unsuccessful", "cancelled"}) and "active" not in awards_statuses:
                    stays_at_qualification = True

            self.recalculate_period_and_change_tender_status(tender, stays_at_qualification)
        else:
            awards = tender.get("awards", [])
            awards_statuses = {award["status"] for award in awards}
            if not awards or awards_statuses.intersection({"cancelled"}):
                all_bids = self.prepare_bids_for_awarding(tender, tender.get("bids", []), lot_id=None)
                bids = self.filter_bids_for_creating_new_awards(awards, all_bids)
                if bids:
                    for bid in bids:
                        self.tender_append_award(tender, bid, all_bids)
                    request = get_request()
                    route_prefix = ProcurementMethodTypePredicate.route_prefix(request)
                    request.response.headers["Location"] = request.route_url(
                        "{}:Tender Awards".format(route_prefix),
                        tender_id=tender["_id"],
                        award_id=tender["awards"][-1]["id"],
                    )
                    awards_statuses.add("pending")

            stays_at_qualification = (
                awards_statuses.difference({"unsuccessful", "cancelled"}) and "active" not in awards_statuses
            )
            self.recalculate_period_and_change_tender_status(tender, stays_at_qualification)

    def recalculate_period_and_change_tender_status(self, tender, stays_at_qualification):
        if stays_at_qualification:
            if tender["status"] != "active.qualification":
                tender["awardPeriod"].pop("endDate", None)
                self.get_change_tender_status_handler("active.qualification")(tender)
        else:
            if tender["status"] != "active.awarded":
                tender["awardPeriod"]["endDate"] = get_request_now().isoformat()
                self.get_change_tender_status_handler("active.awarded")(tender)

    @staticmethod
    def filter_bids_for_creating_new_awards(awards, bids):
        """
        Filer bids for creating new awards in case hasAwardingOrder = False.
        Filter cancelled awards of tender or particular lot and check whether there is no award with the same
        bid_id already generated. If not, than exclude only unsuccessful awards.
        """
        if awards:
            # get bid ids of cancelled awards
            cancelled_award_bid_ids = {award["bid_id"] for award in awards if award["status"] == "cancelled"}
            # exclude bid ids with another awards statuses (if award has already been generated after cancelling)
            cancelled_award_bid_ids = cancelled_award_bid_ids.difference(
                {award["bid_id"] for award in awards if award["status"] != "cancelled"}
            )
            return [bid for bid in bids if bid["id"] in cancelled_award_bid_ids]
        return bids

    def sort_bids(self, tender, bids):
        if all("weightedValue" in bid for bid in bids):
            awarding_criteria_container = "weightedValue"
        else:
            awarding_criteria_container = "value"

        def awarding_criteria_func(bid):
            awarding_criteria = Decimal(bid[awarding_criteria_container][self.awarding_criteria_key])
            return [1, -1][self.reverse_awarding_criteria] * awarding_criteria, bid["date"]

        return sorted(bids, key=awarding_criteria_func)

    def prepare_bids_for_awarding(self, tender, bids, lot_id=None):
        """
        Used by add_next_award method
        :param tender:
        :param bids
        :param lot_id:
        :return: list of bid dict objects sorted in a way they will be selected as winners
        """
        active_bids = []
        for bid in bids:
            if bid["status"] == "active":
                if lot_id:
                    for lot_value in bid["lotValues"]:
                        if (
                            lot_value["relatedLot"] == lot_id
                            and get_lot_value_status(lot_value, bid) in self.active_bid_statuses
                        ):
                            active_bid = {
                                "id": bid["id"],
                                "value": lot_value["value"],
                                "tenderers": bid["tenderers"],
                                "date": lot_value["date"],
                            }
                            if lot_value.get("weightedValue"):
                                weighted_value = lot_value["weightedValue"]
                            else:
                                # Fallback for tenders with no weightedValue precalculated
                                weighted_value = self.calc_weighted_value(tender, bid, lot_value, lot_id)
                            if weighted_value:
                                active_bid["weightedValue"] = weighted_value
                            active_bids.append(active_bid)
                            continue  # only one lotValue in a bid is expected
                else:
                    active_bid = {
                        "id": bid["id"],
                        "value": bid["value"],
                        "tenderers": bid["tenderers"],
                        "date": bid["date"],
                    }
                    if bid.get("weightedValue"):
                        weighted_value = bid["weightedValue"]
                    else:
                        # Fallback for tenders with no weightedValue precalculated
                        weighted_value = self.calc_weighted_value(tender, bid, bid)
                    if weighted_value:
                        active_bid["weightedValue"] = weighted_value
                    active_bids.append(active_bid)
        result = self.sort_bids(tender, active_bids)
        return result

    def exclude_unsuccessful_awarded_bids(self, tender, bids, lot_id):
        # all awards in case of non-lot tender
        lot_awards = (i for i in tender.get("awards", "") if i.get("lotID") == lot_id)
        ignore_bid_ids = tuple(b["bid_id"] for b in lot_awards if b["status"] == "unsuccessful")
        bids = tuple(b for b in bids if b["id"] not in ignore_bid_ids)
        return bids

    def get_mean_value_tendering_bids(self, tender, bids, lot_id, exclude_bid_id):
        before_auction_bids = get_bids_before_auction_results_context()
        before_auction_bids = activate_bids(before_auction_bids)
        before_auction_bids = self.prepare_bids_for_awarding(
            tender,
            before_auction_bids,
            lot_id=lot_id,
        )
        initial_amounts = {b["id"]: float(b["value"]["amount"]) for b in before_auction_bids}
        initial_values = [initial_amounts[b["id"]] for b in bids if b["id"] != exclude_bid_id]
        mean_value = sum(initial_values) / float(len(initial_values))
        return mean_value

    def prepare_award_milestones(self, tender, bid, all_bids, lot_id=None):
        """
        :param tender:
        :param bid: a bid to check
        :param all_bids: prepared the way that "value" key exists even for multi-lot
        :param lot_id:
        :return:
        """
        milestones = []

        if not self.generate_award_milestones:
            # skipping if disabled for the procedure
            return milestones

        if not tender_created_after_2020_rules():
            # skipping for old tenders
            return milestones

        def ratio_of_two_values(v1, v2):
            return 1 - Decimal(v1) / Decimal(v2)

        if len(all_bids) > 1:
            reasons = []
            amount = bid["value"]["amount"]

            #  1st criteria
            mean_value = self.get_mean_value_tendering_bids(
                tender,
                all_bids,
                lot_id=lot_id,
                exclude_bid_id=bid["id"],
            )
            if mean_value and ratio_of_two_values(amount, mean_value) >= Decimal("0.4"):
                reasons.append(ALP_MILESTONE_REASONS[0])

            # 2nd criteria
            for n, b in enumerate(all_bids):
                if b["id"] == bid["id"]:
                    index = n
                    break
            else:
                # should never happen
                raise AssertionError("Selected bid not in the full list")

            following_index = index + 1
            if following_index < len(all_bids):  # selected bid has the following one
                following_bid = all_bids[following_index]
                following_amount = following_bid["value"]["amount"]
                if following_amount and ratio_of_two_values(amount, following_amount) >= Decimal("0.3"):
                    reasons.append(ALP_MILESTONE_REASONS[1])
            if reasons:
                milestones.append({"code": "alp", "description": " / ".join(reasons)})
        return milestones

    def tender_append_award(self, tender, bid, all_bids, lot_id=None):
        """
        Replacement for Tender.append_award method
        :param tender:
        :param bid:
        :param all_bids:
        :param lot_id:
        :return:
        """
        award_data = {
            "bid_id": bid["id"],
            "lotID": lot_id,
            "status": "pending",
            "date": get_request_now(),
            "value": bid["value"],
            "suppliers": bid["tenderers"],
            "period": {
                "startDate": get_request_now().isoformat(),
                "endDate": calculate_tender_full_date(
                    get_request_now(),
                    timedelta(days=self.award_period_duration),
                    tender=tender,
                    working_days=True,
                ).isoformat(),
            },
        }
        if "weightedValue" in bid:
            award_data["weightedValue"] = bid["weightedValue"]

        # append an "alp" milestone if it's the case
        if hasattr(self.award_class, "milestones"):
            milestones = self.prepare_award_milestones(tender, bid, all_bids, lot_id)
            if milestones:
                award_data["milestones"] = milestones

        if "awards" not in tender:
            tender["awards"] = []

        award = self.award_class(award_data)
        tender["awards"].append(award.serialize())

    @classmethod
    def calc_weighted_value(cls, tender: dict, bid: dict, value_container: dict, lot_id: str = None) -> Optional[dict]:
        value = value_container.get("value", {})

        if not value:
            # for example competitiveDialogueUA and competitiveDialogueEU
            # doesn't have value in bid or in lotValues
            return None

        weighted_value = {}

        value_amount = float(value.get(cls.awarding_criteria_key))

        denominator = cls.calc_denominator(tender, bid, lot_id)
        if denominator is not None:
            if cls.reverse_awarding_criteria:
                value_amount = value_amount * denominator
            else:
                value_amount = value_amount / denominator
            weighted_value["denominator"] = denominator

        addition = cls.calc_addition(tender, bid, lot_id)
        if addition is not None:
            if cls.reverse_awarding_criteria:
                value_amount = value_amount - addition
            else:
                value_amount = value_amount + addition
            weighted_value["addition"] = round(addition, 2)

        if weighted_value:
            weighted_value[cls.awarding_criteria_key] = round(value_amount, 2)
            weighted_value["currency"] = value_container["value"]["currency"]
            return weighted_value

        return None

    @staticmethod
    def calc_addition(tender: dict, bid: dict, lot_id: str = None) -> Optional[float]:
        """
        Calculates addition for weighted value for: LCC
        """
        criteria = tender.get("criteria", [])
        responses = bid.get("requirementResponses", [])

        if not criteria:
            # nothing to do here
            return None

        lcc_criteria = []
        for criterion in criteria:
            classification = criterion.get("classification", {})
            if classification.get("id") in CRITERION_LIFE_CYCLE_COST_IDS:
                lcc_criteria.append(criterion)

        if not lcc_criteria:
            # no lcc features at all
            return None

        if lot_id:
            filtered_criteria = []
            for criterion in lcc_criteria:
                if criterion.get("relatesTo") == "lot" and criterion.get("relatedItem") != lot_id:
                    continue
                filtered_criteria.append(criterion)
        else:
            filtered_criteria = lcc_criteria

        if not filtered_criteria:
            # no lcc features for lot
            return None

        filtered_responses = []
        for response in responses:
            for criterion in filtered_criteria:
                for group in criterion.get("requirementGroups", []):
                    for requirement in group.get("requirements", []):
                        if requirement["id"] == response["requirement"]["id"]:
                            filtered_responses.append(response)

        addition = sum(float(response.get("value") or 0) for response in filtered_responses)
        return addition

    @classmethod
    def calc_denominator(cls, tender: dict, bid: dict, lot_id: str = None) -> Optional[float]:
        """
        Calculates denominator for weighted value for: features
        """
        features = tender.get("features", [])
        items = tender.get("items", [])
        parameters = bid.get("parameters", [])

        if not features:
            # no features at all
            return None

        if lot_id:
            filtered_features = filter_features(features, items, lot_ids=[lot_id])
        else:
            filtered_features = features

        if not filtered_features:
            # no features for lot
            return None

        filtered_features_codes = [i["code"] for i in filtered_features]
        filtered_parameters = [param for param in parameters if param["code"] in filtered_features_codes]

        denominator = float(calculate_coeficient(filtered_features, filtered_parameters))
        return denominator
