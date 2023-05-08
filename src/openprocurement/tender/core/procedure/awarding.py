from decimal import Decimal
from logging import getLogger
from typing import Optional

from barbecue import calculate_coeficient

from openprocurement.api.context import get_now
from openprocurement.api.constants import (
    RELEASE_2020_04_19,
    TENDER_WEIGHTED_VALUE_PRE_CALCULATION,
)
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.context import (
    get_request,
    get_tender,
    get_bids_before_auction_results_context,
)
from openprocurement.tender.core.procedure.utils import (
    get_first_revision_date,
    filter_features,
)
from openprocurement.tender.core.constants import (
    ALP_MILESTONE_REASONS,
    CRITERION_LIFE_CYCLE_COST_IDS,
)

LOGGER = getLogger(__name__)


class TenderStateAwardingMixing:
    award_class = Award
    get_change_tender_status_handler: callable
    set_object_status: callable
    awarding_criteria_key: str = "amount"
    reverse_awarding_criteria: bool = False

    def add_next_award(self):
        tender = get_tender()
        now = get_now()

        tender["awardPeriod"] = award_period = tender.get("awardPeriod", {})
        if "startDate" not in award_period:
            award_period["startDate"] = now.isoformat()

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
                        self.tender_append_award(tender, self.award_class, bids[0], all_bids, lot_id=lot["id"])
                        request = get_request()
                        request.response.headers["Location"] = request.route_url(
                            "{}:Tender Awards".format(tender["procurementMethodType"]),
                            tender_id=tender["_id"],
                            award_id=tender["awards"][-1]["id"]
                        )
                        statuses.add("pending")
                    else:
                        statuses.add("unsuccessful")
                else:
                    self.set_object_status(lot, "unsuccessful")
                    statuses.add("unsuccessful")

            if statuses.difference({"unsuccessful", "active"}):
                if tender["status"] != "active.qualification":
                    tender["awardPeriod"].pop("endDate", None)
                    self.get_change_tender_status_handler("active.qualification")(tender)
            else:
                if tender["status"] != "active.awarded":
                    tender["awardPeriod"]["endDate"] = now.isoformat()
                    self.get_change_tender_status_handler("active.awarded")(tender)
        else:
            awards = tender.get("awards")
            if not awards or awards[-1]["status"] not in ("pending", "active"):
                all_bids = self.prepare_bids_for_awarding(tender, tender.get("bids", []), lot_id=None)
                bids = self.exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=None)
                if bids:
                    self.tender_append_award(tender, self.award_class, bids[0], all_bids)
                    request = get_request()
                    request.response.headers["Location"] = request.route_url(
                        "{}:Tender Awards".format(tender["procurementMethodType"]),
                        tender_id=tender["_id"],
                        award_id=tender["awards"][-1]["id"]
                    )
            if tender["awards"][-1]["status"] == "pending":
                if tender["status"] != "active.qualification":
                    tender["awardPeriod"].pop("endDate", None)
                    self.get_change_tender_status_handler("active.qualification")(tender)
            else:
                if tender["status"] != "active.awarded":
                    tender["awardPeriod"]["endDate"] = now.isoformat()
                    self.get_change_tender_status_handler("active.awarded")(tender)

    def sort_bids(self, tender, bids):
        if all("weightedValue" in bid for bid in bids):
            awarding_criteria_container = "weightedValue"
        else:
            awarding_criteria_container = "value"

        def awarding_criteria_func(bid):
            awarding_criteria = Decimal(bid[awarding_criteria_container][self.awarding_criteria_key])
            return [1, -1][self.reverse_awarding_criteria] * awarding_criteria, bid["date"]

        return sorted(bids, key=awarding_criteria_func)

    def prepare_bids_for_awarding(
        self,
        tender,
        bids,
        lot_id=None,
    ):
        """
        Used by add_next_award method
        :param tender:
        :param bids
        :param lot_id:
        :param reverse_awarding_criteria: Param to configure award criteria
            Default configuration for awarding is reversed (from lower to higher)
            When False, awards are generated from lower to higher by value.amount
            When True, awards are generated from higher to lower by value.amount
        :return: list of bid dict objects sorted in a way they will be selected as winners
        """
        active_bids = []
        for bid in bids:
            if bid["status"] == "active":
                if lot_id:
                    for lot_value in bid["lotValues"]:
                        if lot_value["relatedLot"] == lot_id and lot_value.get("status", "active") == "active":
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
        before_auction_bids = self.prepare_bids_for_awarding(
            tender, before_auction_bids, lot_id=lot_id,
        )
        initial_amounts = {
            b["id"]: float(b["value"]["amount"])
            for b in before_auction_bids
        }
        initial_values = [
            initial_amounts[b["id"]]
            for b in bids
            if b["id"] != exclude_bid_id  # except the bid being checked
        ]
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
        skip_method_types = (
            "belowThreshold",
            "priceQuotation",
            "esco",
            "aboveThresholdUA.defense",
            "simple.defense"
        )

        if (
            tender.get("procurementMethodType", "") in skip_method_types
            or get_first_revision_date(tender, default=get_now()) < RELEASE_2020_04_19
        ):
            return milestones   # skipping

        def ratio_of_two_values(v1, v2):
            return 1 - Decimal(v1) / Decimal(v2)

        if len(all_bids) > 1:
            reasons = []
            amount = bid["value"]["amount"]
            #  1st criteria
            mean_value = self.get_mean_value_tendering_bids(
                tender, all_bids, lot_id=lot_id, exclude_bid_id=bid["id"],
            )
            if ratio_of_two_values(amount, mean_value) >= Decimal("0.4"):
                reasons.append(ALP_MILESTONE_REASONS[0])

            # 2nd criteria
            for n, b in enumerate(all_bids):
                if b["id"] == bid["id"]:
                    index = n
                    break
            else:
                raise AssertionError("Selected bid not in the full list")  # should never happen
            following_index = index + 1
            if following_index < len(all_bids):  # selected bid has the following one
                following_bid = all_bids[following_index]
                following_amount = following_bid["value"]["amount"]
                if ratio_of_two_values(amount, following_amount) >= Decimal("0.3"):
                    reasons.append(ALP_MILESTONE_REASONS[1])
            if reasons:
                milestones.append(
                    {
                        "code": "alp",
                        "description": " / ".join(reasons)
                    }
                )
        return milestones

    def tender_append_award(self, tender, award_class, bid, all_bids, lot_id=None):
        """
        Replacement for Tender.append_award method
        :param award_class:
        :param bid:
        :param all_bids:
        :param lot_id:
        :return:
        """
        now = get_now()
        award_data = {
            "bid_id": bid["id"],
            "lotID": lot_id,
            "status": "pending",
            "date": now,
            "value": bid["value"],
            "suppliers": bid["tenderers"],
        }
        if "weightedValue" in bid:
            award_data["weightedValue"] = bid["weightedValue"]
        # append an "alp" milestone if it's the case
        if hasattr(award_class, "milestones"):
            milestones = self.prepare_award_milestones(tender, bid, all_bids, lot_id)
            if milestones:
                award_data["milestones"] = milestones

        if "awards" not in tender:
            tender["awards"] = []

        award = award_class(award_data)
        tender["awards"].append(award.serialize())

    def calc_bids_weighted_values(self, tender):
        if not TENDER_WEIGHTED_VALUE_PRE_CALCULATION:
            return

        bids = tender.get("bids", "")

        for bid in bids:
            if bid.get("lotValues", ""):
                for lot_value in bid["lotValues"]:
                    lot_id = lot_value["relatedLot"]
                    weighted_value = self.calc_weighted_value(tender, bid, lot_value, lot_id)
                    if weighted_value:
                        lot_value["weightedValue"] = weighted_value
            else:
                weighted_value = self.calc_weighted_value(tender, bid, bid)
                if weighted_value:
                    bid["weightedValue"] = weighted_value

    @classmethod
    def calc_weighted_value(
        cls,
        tender: dict,
        bid: dict,
        value_container: dict,
        lot_id: str = None,
    ) -> Optional[dict]:
        features = tender.get("features", "")
        items = tender.get("items", "")
        criteria = tender.get("criteria", "")
        parameters = bid.get("parameters", "")
        responses = bid.get("requirementResponses", "")

        value = value_container.get("value", {})

        if not value:
            # for example competitiveDialogueUA and competitiveDialogueEU
            # doesn't have value in bid or in lotValues
            return None

        value_amount = float(value.get(cls.awarding_criteria_key))

        weighted_value = {}

        denominator = cls.calc_denominator(parameters, features, items, lot_id)
        if denominator is not None:
            if cls.reverse_awarding_criteria:
                value_amount = value_amount * denominator
            else:
                value_amount = value_amount / denominator
            weighted_value["denominator"] = denominator

        addition = cls.calc_addition(criteria, responses, lot_id)
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
    def calc_addition(
        criteria: list,
        responses: list,
        lot_id: str = None,
    ) -> Optional[float]:
        """
        Calculates addition for weighted value for: LCC
        :param criteria:
        :param responses:
        :param lot_id:
        :return:
        """
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
            # no lcc features
            # either in tender for non-lot tenders
            # or in lot for lot tenders
            return None

        filtered_responses = []
        for response in responses:
            for criterion in filtered_criteria:
                for group in criterion.get("requirementGroups", []):
                    for requirement in group.get("requirements", []):
                        if requirement["id"] == response["requirement"]["id"]:
                            filtered_responses.append(response)

        addition = sum(float(response.get("value")) for response in filtered_responses)
        return addition

    @classmethod
    def calc_denominator(
        cls,
        parameters: list,
        features: list = "",
        items: list = "",
        lot_id: str = None,
    ) -> Optional[float]:
        """
        Calculates denominator for weighted value for: features
        :param parameters:
        :param features:
        :param items:
        :param lot_id:
        :return:
        """
        if not features:
            # nothing to do here
            return None

        if lot_id:
            filtered_features = filter_features(features, items, lot_ids=[lot_id])
        else:
            filtered_features = features

        if not filtered_features:
            # no features
            # either in tender for non-lot tenders
            # or in lot for lot tenders
            return None

        filtered_features_codes = [i["code"] for i in filtered_features]
        filtered_parameters = [param for param in parameters if param["code"] in filtered_features_codes]

        denominator = float(calculate_coeficient(filtered_features, filtered_parameters))
        return denominator
