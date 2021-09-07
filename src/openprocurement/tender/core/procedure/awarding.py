from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.context import get_now, get_request
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import context_unpack
from openprocurement.tender.core.constants import (
    ALP_MILESTONE_REASONS,
    AWARD_CRITERIA_LIFE_CYCLE_COST,
)
from jsonpointer import JsonPointerException
from jsonpatch import JsonPatchException, apply_patch as apply_json_patch
from functools import partial
from barbecue import chef
from decimal import Decimal
from copy import deepcopy
from logging import getLogger
import jmespath


LOGGER = getLogger(__name__)


def sort_bids(tender, bids, features=None):
    configurator = get_request().content_configurator
    if features:
        # convert features.enum.value  to float, otherwise may fail; Failed in cfaua tests
        features = deepcopy(features)
        for f in features:
            for e in f["enum"]:
                e["value"] = float(e["value"])
        bids = chef(
            bids,
            features=features,
            ignore=[],  # filters by id, shouldn't be a part of this lib
            reverse=configurator.reverse_awarding_criteria,
            awarding_criteria_key=configurator.awarding_criteria_key,
        )
    else:
        award_criteria_path = f"value.{configurator.awarding_criteria_key}"
        if tender.get("awardCriteria") == AWARD_CRITERIA_LIFE_CYCLE_COST:
            def awarding_criteria_func(bid):
                awarding_criteria = jmespath.search("weightedValue.amount", bid)
                if not awarding_criteria:
                    awarding_criteria = jmespath.search(award_criteria_path, bid)
                return Decimal(awarding_criteria)
        else:
            def awarding_criteria_func(bid):
                awarding_criteria = jmespath.search(award_criteria_path, bid)
                return Decimal(awarding_criteria)
        bids = sorted(bids, key=lambda bid: (
            [1, -1][configurator.reverse_awarding_criteria] * awarding_criteria_func(bid), bid['date']
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


def prepare_bids_for_awarding(tender, bids, lot_id=None):
    """
    Used by add_next_award method
    :param tender:
    :param bids
    :param lot_id:
    :return: list of bid dict objects sorted in a way they will be selected as winners
    """
    features = filter_features(tender.get("features"), tender.get("items", []), lot_ids=[lot_id])
    codes = [i["code"] for i in features]
    active_bids = []
    for bid in bids:
        if bid["status"] == "active":
            bid_params = [i for i in bid.get("parameters", "")
                          if i["code"] in codes]
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
    result = sort_bids(tender, active_bids, features)
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
    before_auction_bids = get_bids_before_auction_results(tender)
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
        getattr(tender, "procurementMethodType", "") in skip_method_types
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
        award_data["milestones"] = prepare_award_milestones(tender, bid, all_bids, lot_id)

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


def add_next_award(request, award_class=Award):
    tender = request.validated["tender"]
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

            lot_awards = tuple(a for a in tender.get("awards", "")
                               if a["lotID"] == lot["id"])
            if lot_awards and lot_awards[-1]["status"] in ["pending", "active"]:
                statuses.add(lot_awards[-1]["status"])
                continue

            all_bids = prepare_bids_for_awarding(tender, tender.get("bids", []), lot_id=lot["id"])
            if all_bids:
                bids = exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=lot["id"])
                if bids:
                    tender_append_award(tender, award_class, bids[0], all_bids, lot_id=lot["id"])
                    request.response.headers["Location"] = request.route_url(
                        "{}:Tender Awards".format(tender["procurementMethodType"]),
                        tender_id=tender["_id"],
                        award_id=tender["awards"][-1]["id"]
                    )
                    statuses.add("pending")
                else:
                    statuses.add("unsuccessful")
            else:
                lot["status"] = "unsuccessful"
                statuses.add("unsuccessful")

        if statuses.difference({"unsuccessful", "active"}):
            tender["awardPeriod"]["endDate"] = None
            tender["status"] = "active.qualification"
        else:
            tender["awardPeriod"]["endDate"] = now.isoformat()
            tender["status"] = "active.awarded"
    else:
        awards = tender.get("awards")
        if not awards or awards[-1]["status"] not in ("pending", "active"):
            all_bids = prepare_bids_for_awarding(tender, tender.get("bids", []), lot_id=None)
            bids = exclude_unsuccessful_awarded_bids(tender, all_bids, lot_id=None)
            if bids:
                tender_append_award(tender, award_class, bids[0], all_bids)
                request.response.headers["Location"] = request.route_url(
                    "{}:Tender Awards".format(tender["procurementMethodType"]),
                    tender_id=tender["_id"],
                    award_id=tender["awards"][-1]["id"]
                )
        if tender["awards"][-1]["status"] == "pending":
            tender["awardPeriod"]["endDate"] = None
            tender["status"] = "active.qualification"
        else:
            tender["awardPeriod"]["endDate"] = now.isoformat()
            tender["status"] = "active.awarded"


def cleanup_bids_for_cancelled_lots(tender):
    cancelled_lots = tuple(i["id"] for i in tender.get("lots", "") if i["status"] == "cancelled")
    if cancelled_lots:
        return
    cancelled_items = [i["id"] for i in tender.get("items", "") if i["relatedLot"] in cancelled_lots]
    cancelled_features = [
        i["code"]
        for i in tender.get("features", "")
        if i["featureOf"] == "lot" and i["relatedItem"] in cancelled_lots
        or i["featureOf"] == "item" and i["relatedItem"] in cancelled_items
    ]
    for bid in tender.get("bids", ""):
        bid["documents"] = [i for i in bid.get("documents", "")
                            if i.get("documentOf") != "lot" or i.get("relatedItem") not in cancelled_lots]
        bid["parameters"] = [i for i in bid.get("parameters", "") if i["code"] not in cancelled_features]
        bid["lotValues"] = [i for i in bid.get("lotValues", "") if i["relatedLot"] not in cancelled_lots]
        if not bid["lotValues"]:
            tender["bids"].remove(bid)
