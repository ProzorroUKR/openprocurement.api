from operator import itemgetter

from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.auction import PreQualificationShouldStartAfterMixing
from openprocurement.tender.core.procedure.context import get_now, get_request
from openprocurement.tender.openeu.procedure.models.award import Award
from openprocurement.tender.core.procedure.models.qualification import Qualification
from openprocurement.tender.core.constants import CRITERION_LIFE_CYCLE_COST_IDS
from openprocurement.tender.openeu.utils import is_procedure_restricted


class BaseOpenEUTenderState(PreQualificationShouldStartAfterMixing, TenderState):
    award_class = Award
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    def tendering_end_handler(self, tender):

        for complaint in tender.get("complaints", ""):
            if complaint.get("status") == "answered" and complaint.get("resolutionType"):
                self.set_object_status(complaint, complaint["resolutionType"])

        handler = self.get_change_tender_status_handler("active.pre-qualification")
        handler(tender)
        tender["qualificationPeriod"] = {"startDate": get_now().isoformat()}

        self.remove_draft_bids(tender)
        self.check_bids_number(tender)
        self.prepare_qualifications(tender)

    def prepare_qualifications(self, tender):
        if "qualifications" not in tender:
            tender["qualifications"] = []
        bids = tender.get("bids", "")
        lots = tender.get("lots")
        if lots:
            active_lots = tuple(lot["id"] for lot in lots if lot["status"] == "active")
            for bid in bids:
                if bid.get("status") not in ("invalid", "deleted"):
                    for lotValue in bid.get("lotValues", ""):
                        if lotValue.get("status", "pending") == "pending" and lotValue["relatedLot"] in active_lots:
                            qualification = Qualification({
                                "bidID": bid["id"],
                                "status": "pending",
                                "lotID": lotValue["relatedLot"],
                                "date": get_now().isoformat()
                            }).serialize()
                            tender["qualifications"].append(qualification)
        else:
            for bid in bids:
                if bid["status"] == "pending":
                    qualification = Qualification({
                        "bidID": bid["id"],
                        "status": "pending",
                        "date": get_now().isoformat()
                    }).serialize()
                    tender["qualifications"].append(qualification)

    def cancellation_compl_period_end_handler(self, cancellation):
        def handler(tender):
            self.set_object_status(cancellation, "active")
            if cancellation.get("relatedLot"):
                # 1
                related_lot = cancellation["relatedLot"]
                for lot in tender["lots"]:
                    if lot["id"] == related_lot:
                        self.set_object_status(lot, "cancelled")

                # 2
                cancelled_lots = {i["id"] for i in tender.get("lots") if i["status"] == "cancelled"}
                cancelled_items = {i["id"] for i in tender.get("items", "")
                                   if i.get("relatedLot") in cancelled_lots}
                cancelled_features = {
                    i["code"]
                    for i in tender.get("features", "")
                    if i["featureOf"] == "lot" and i["relatedItem"] in cancelled_lots
                    or i["featureOf"] == "item" and i["relatedItem"] in cancelled_items
                }

                # 3
                if tender["status"] in (
                    "active.tendering",
                    "active.pre-qualification",
                    "active.pre-qualification.stand-still",
                    "active.auction",
                ):
                    for bid in tender.get("bids", ""):
                        bid["parameters"] = [i for i in bid.get("parameters", "")
                                             if i["code"] not in cancelled_features]
                        bid["lotValues"] = [i for i in bid.get("lotValues", "")
                                            if i["relatedLot"] not in cancelled_lots]
                        if not bid["lotValues"] and bid["status"] in ["pending", "active"]:
                            if tender["status"] == "active.tendering":
                                bid["status"] = "invalid"
                            else:
                                bid["status"] = "invalid.pre-qualification"

                # 4
                lot_statuses = {lot["status"] for lot in tender["lots"]}
                if lot_statuses == {"cancelled"}:
                    self.get_change_tender_status_handler("cancelled")(tender)
                elif not lot_statuses.difference({"unsuccessful", "cancelled"}):
                    self.get_change_tender_status_handler("unsuccessful")(tender)
                elif not lot_statuses.difference({"complete", "unsuccessful", "cancelled"}):
                    self.get_change_tender_status_handler("complete")(tender)

                # 5
                if tender["status"] == "active.auction" and all(
                        i.get("auctionPeriod", {}).get("endDate")
                        for i in tender["lots"]
                        if i["status"] == "active"   # TODO: no checks for bids count (like in core method)
                ):
                    self.add_next_award()
            else:
                if tender["status"] == "active.tendering":
                    tender["bids"] = []
                elif tender["status"] in (
                    "active.pre-qualification",
                    "active.pre-qualification.stand-still",
                    "active.auction",
                ):
                    for bid in tender.get("bids", ""):
                        if bid["status"] in ("pending", "active"):
                            bid["status"] = "invalid.pre-qualification"
                            # which doesn't delete data, but they are hidden by serialization functionality
                self.get_change_tender_status_handler("cancelled")(tender)
        return handler

    def invalidate_bids_data(self, tender):
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"

    def pre_qualification_stand_still_ends_handler(self, tender):
        handler = self.get_change_tender_status_handler("active.auction")
        handler(tender)
        self.check_bids_number(tender)


class OpenEUTenderState(BaseOpenEUTenderState):
    def tendering_end_handler(self, tender):
        if is_procedure_restricted(tender):
            self.min_bids_number = tender.get("preQualificationMinBidsNumber", 4)
        super().tendering_end_handler(tender)
        self.calculate_bids_weighted_values(tender)

    def calculate_bids_weighted_values(self, tender):
        def _calc_denominator(parameters: list, features: list = "", lot_id: str = None) -> float:
            if lot_id:
                features_codes = [
                    i["code"]
                    for i in features
                    if i.get("featureOf", "") == "lot" and i.get("relatedItem") == lot_id
                ]
                params_sum = sum(param["value"] for param in parameters if param["code"] in features_codes)
            else:
                params_sum = sum(param["value"] for param in parameters)
            return 1 / (1 - params_sum)

        def _set_weighted_value(value_container: dict, addition: float = 0, denominator: float = 1) -> None:
            value_amount = float(value_container.get("value", {}).get("amount", 0))
            weighted_value = {"amount": round((value_amount / denominator) + addition, 2)}
            if addition:
                weighted_value["addition"] = round(addition, 2)
            if denominator != 1:
                weighted_value["denominator"] = denominator

            if "addition" in weighted_value or "denominator" in weighted_value:
                weighted_value.update({
                    "currency": value_container["value"]["currency"],
                    "valueAddedTaxIncluded": value_container["value"]["valueAddedTaxIncluded"],
                })
                value_container["weightedValue"] = weighted_value

        bids = tender.get("bids", "")
        features = tender.get("features", "")

        lcc_requirement_ids = [
            req["id"]
            for c in tender.get("criteria", "")
            for rg in c.get("requirementGroups", "")
            for req in rg.get("requirements", "")
            if c["classification"]["id"] in CRITERION_LIFE_CYCLE_COST_IDS
        ]

        for bid in bids:

            parameters = bid.get("parameters", "")

            if not (parameters or lcc_requirement_ids):
                continue

            addition = 0
            if lcc_requirement_ids:
                addition = sum(
                    float(req_response.get("value"))
                    for req_response in bid.get("requirementResponses", "")
                    if req_response["requirement"]["id"] in lcc_requirement_ids
                )

            if bid.get("lotValues", ""):
                for lot_value in bid["lotValues"]:
                    denominator = _calc_denominator(parameters, features, lot_value["relatedLot"])
                    _set_weighted_value(lot_value, addition=addition, denominator=denominator)
            else:
                denominator = _calc_denominator(parameters)
                _set_weighted_value(bid, addition=addition, denominator=denominator)

    def pre_qualification_stand_still_ends_handler(self, tender):
        if is_procedure_restricted(tender):
            self.min_bids_number = tender.get("preQualificationMinBidsNumber", 4)

        super().pre_qualification_stand_still_ends_handler(tender)

        if is_procedure_restricted(tender):
            self.qualification_bids_by_rating(tender)

    def qualification_bids_by_rating(self, tender):
        self.min_bids_number = tender.get("preQualificationMinBidsNumber", 4)

        bid_limit = tender.get("preQualificationFeaturesRatingBidLimit")
        bids = tender.get("bids", "")

        if not bid_limit:
            return

        bids_with_sum_params = [
            (bid, sum(param["value"] for param in bid.get("parameters", "")))
            for bid in bids
        ]
        sorted_bids = sorted(bids_with_sum_params, key=itemgetter(1), reverse=True)

        for bid, _ in sorted_bids[bid_limit:]:
            bid["status"] = "unsuccessful"
