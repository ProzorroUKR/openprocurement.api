from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.context import (
    get_now,
    get_request,
    get_tender,
    get_bids_before_auction_results_context,
)
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import context_unpack
from openprocurement.tender.core.constants import (
    ALP_MILESTONE_REASONS,
    AWARD_CRITERIA_LIFE_CYCLE_COST,
)
from jsonpointer import JsonPointerException
from jsonpatch import JsonPatchException, apply_patch as apply_json_patch
from barbecue import chef
from decimal import Decimal
from copy import deepcopy
from logging import getLogger
import jmespath


LOGGER = getLogger(__name__)


def sort_bids(
    tender,
    bids,
    features=None,
    reverse_awarding_criteria=False,
):
    if all("weightedValue" in bid for bid in bids):
        bids = sorted(bids, key=lambda bid: (
            [1, -1][reverse_awarding_criteria] * bid["weightedValue"]["amount"], bid['date']
        ))
    elif features:
        # TODO: Deprecated, remove this "if" block
        features = deepcopy(features)
        for f in features:
            for e in f["enum"]:
                # convert features.enum.value to float, otherwise may fail
                # Failed in cfaua tests
                e["value"] = float(e["value"])
        bids = chef(
            bids,
            features=features,
            ignore=[],
            reverse=reverse_awarding_criteria,
            awarding_criteria_key="amount",
        )
    else:
        bids = sorted(bids, key=lambda bid: (
            [1, -1][reverse_awarding_criteria] * bid["value"]["amount"], bid['date']
        ))
    return bids


def filter_features(features, items, lot_ids=None):
    lot_ids = lot_ids or [None]
    lot_items = [
        i["id"]
        for i in items
        if i.get("relatedLot") in lot_ids
    ]  # all items in case of non-lot tender
    features = [
        feature
        for feature in (features or tuple())
        if any((
            feature["featureOf"] == "tenderer",
            feature["featureOf"] == "lot" and feature["relatedItem"] in lot_ids,
            feature["featureOf"] == "item" and feature["relatedItem"] in lot_items,
        ))
    ]  # all features in case of non-lot tender
    return features


def prepare_bids_for_awarding(
    tender,
    bids,
    lot_id=None,
    reverse_awarding_criteria=False,
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
    features = filter_features(tender.get("features"), tender.get("items", []), lot_ids=[lot_id])
    codes = [i["code"] for i in features]
    active_bids = []
    for bid in bids:
        if bid["status"] == "active":
            bid_params = [i for i in bid.get("parameters", "") if i["code"] in codes]
            if lot_id:
                for lot_value in bid["lotValues"]:
                    if lot_value["relatedLot"] == lot_id and lot_value.get("status", "active") == "active":
                        active_bid = {
                            "id": bid["id"],
                            "value": lot_value["value"],
                            "tenderers": bid["tenderers"],
                            "parameters": bid_params,
                            "date": lot_value["date"],
                        }
                        if lot_value.get("weightedValue"):
                            active_bid["weightedValue"] = lot_value["weightedValue"]
                        active_bids.append(active_bid)
                        continue  # only one lotValue in a bid is expected
            else:
                active_bid = {
                    "id": bid["id"],
                    "value": bid["value"],
                    "tenderers": bid["tenderers"],
                    "parameters": bid_params,
                    "date": bid["date"],
                }
                if bid.get("weightedValue"):
                    active_bid["weightedValue"] = bid["weightedValue"]
                active_bids.append(active_bid)
    result = sort_bids(
        tender,
        active_bids,
        features=features,
        reverse_awarding_criteria=reverse_awarding_criteria,
    )
    return result


# low price milestones
def get_bids_before_auction_results(tender):
    request = get_request()
    initial_doc = request.validated["tender_src"]
    auction_revisions = (revision for revision in reversed(tender.get("revisions", []))
                         if revision["author"] == "auction")
    for revision in auction_revisions:
        try:
            initial_doc = apply_json_patch(initial_doc, revision["changes"])
        except (JsonPointerException, JsonPatchException) as e:
            LOGGER.exception(e, extra=context_unpack(request, {"MESSAGE_ID": "fail_get_tendering_bids"}))
    return deepcopy(initial_doc["bids"])


def get_mean_value_tendering_bids(tender, bids, lot_id, exclude_bid_id):
    before_auction_bids = get_bids_before_auction_results_context()
    before_auction_bids = prepare_bids_for_awarding(
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


def prepare_award_milestones(tender, bid, all_bids, lot_id=None):
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
        mean_value = get_mean_value_tendering_bids(
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


def tender_append_award(tender, award_class, bid, all_bids, lot_id=None):
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
        milestones = prepare_award_milestones(tender, bid, all_bids, lot_id)
        if milestones:
            award_data["milestones"] = milestones

    if "awards" not in tender:
        tender["awards"] = []

    award = award_class(award_data)
    tender["awards"].append(
        award.serialize()
    )


def exclude_unsuccessful_awarded_bids(tender, bids, lot_id):
    # all awards in case of non-lot tender
    lot_awards = (i for i in tender.get("awards", "") if i.get("lotID") == lot_id)
    ignore_bid_ids = tuple(b["bid_id"] for b in lot_awards if b["status"] == "unsuccessful")
    bids = tuple(b for b in bids if b["id"] not in ignore_bid_ids)
    return bids


class TenderStateAwardingMixing:
    award_class = Award
    get_change_tender_status_handler: callable
    set_object_status: callable
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

                all_bids = prepare_bids_for_awarding(
                    tender,
                    tender.get("bids", []),
                    lot_id=lot["id"],
                    reverse_awarding_criteria=self.reverse_awarding_criteria
                )
                if all_bids:
                    bids = exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=lot["id"])
                    if bids:
                        tender_append_award(tender, self.award_class, bids[0], all_bids, lot_id=lot["id"])
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
                all_bids = prepare_bids_for_awarding(
                    tender,
                    tender.get("bids", []),
                    lot_id=None,
                    reverse_awarding_criteria=self.reverse_awarding_criteria
                )
                bids = exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=None)
                if bids:
                    tender_append_award(tender, self.award_class, bids[0], all_bids)
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
