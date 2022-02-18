from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.core.procedure.context import get_request, get_now, get_tender
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.cfaua.constants import (
    TENDERING_EXTRA_PERIOD,
    COMPLAINT_STAND_STILL,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
    QUALIFICATION_COMPLAINT_STAND_STILL,
    PREQUALIFICATION_COMPLAINT_STAND_STILL,
)
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
    calculate_clarif_business_date,
    check_auction_period,
)
from openprocurement.api.utils import raise_operation_error


def all_bids_are_reviewed(tender):
    bids = tender.get("bids", "")
    lots = tender.get("lots")
    if lots:
        active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
        return all(
            lotValue.get("status") != "pending"
            for bid in bids
            if bid.get("status") not in ("invalid", "deleted")
            for lotValue in bid.get("lotValues", "")
            if lotValue["relatedLot"] in active_lots

        )
    else:
        return all(bid.get("status") != "pending" for bid in bids)


def all_awards_are_reviewed(tender):
    """ checks if all tender awards are reviewed
    """
    return all(award["status"] != "pending" for award in tender["awards"])


class CFAUATenderDetailsMixing(TenderDetailsMixing):
    tendering_period_extra = TENDERING_EXTRA_PERIOD

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        # self.initialize_enquiry_period(tender)

    def on_patch(self, before, after):
        # TODO: find a better place for this check, may be a distinct endpoint: PUT /tender/uid/status
        if before["status"] == "active.pre-qualification":
            passed_data = get_request().validated["json_data"]
            if passed_data != {"status": "active.pre-qualification.stand-still"}:
                raise_operation_error(
                    get_request(),
                    "Can't update tender at 'active.pre-qualification' status",
                )
            else:  # switching to active.pre-qualification.stand-still
                lots = after.get("lots")
                if lots:
                    active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
                else:
                    active_lots = {None}

                if any(
                    i["status"] in self.block_complaint_status
                    for q in after["qualifications"]
                    for i in q.get("complaints", "")
                    if q.get("lotID") in active_lots
                ):
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.pre-qualification.stand-still' before resolve all complaints"
                    )

                if all_bids_are_reviewed(after):
                    after["qualificationPeriod"]["endDate"] = calculate_complaint_business_date(
                        get_now(), PREQUALIFICATION_COMPLAINT_STAND_STILL, after
                    ).isoformat()
                    self.check_auction_time(after)
                else:
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.pre-qualification.stand-still' while not all bids are qualified",
                    )

        # before status != active.pre-qualification
        elif after["status"] == "active.pre-qualification.stand-still":
            raise_operation_error(
                get_request(),
                f"Can't switch to 'active.pre-qualification.stand-still' from {before['status']}",
            )

        if before["status"] == "active.qualification":
            passed_data = get_request().validated["json_data"]
            if passed_data != {"status": "active.qualification.stand-still"}:
                raise_operation_error(
                    get_request(),
                    "Can't update tender at 'active.qualification' status",
                )
            else:  # switching to active.pre-qualification.stand-still
                lots = after.get("lots")
                if lots:
                    active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
                else:
                    active_lots = {None}

                if any(
                    i["status"] in self.block_complaint_status
                    for q in after["awards"]
                    for i in q.get("complaints", "")
                    if q.get("lotID") in active_lots
                ):
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.qualification.stand-still' before resolve all complaints"
                    )

                if all_awards_are_reviewed(after):
                    after["awardPeriod"]["endDate"] = calculate_complaint_business_date(
                        get_now(), QUALIFICATION_COMPLAINT_STAND_STILL, after
                    ).isoformat()
                    for award in after["awards"]:
                        if award["status"] != "cancelled":
                            award["complaintPeriod"] = {
                                "startDate": get_now().isoformat(),
                                "endDate": after["awardPeriod"]["endDate"],
                            }
                else:
                    raise_operation_error(
                        get_request(),
                        "Can't switch to 'active.qualification.stand-still' while not all awards are qualified",
                    )

        elif after["status"] == "active.qualification.stand-still":
            raise_operation_error(
                get_request(),
                f"Can't switch to 'active.qualification.stand-still' from {before['status']}",
            )

        self.validate_fields_unchanged(before, after)

        # bid invalidation rules
        if before["status"] == "active.tendering":
            if "tenderPeriod" in after and "endDate" in after["tenderPeriod"]:
                # self.request.validated["tender"].tenderPeriod.import_data(data["tenderPeriod"])
                tendering_end = dt_from_iso(after["tenderPeriod"]["endDate"])
                if calculate_tender_business_date(get_now(), self.tendering_period_extra, after) > tendering_end:
                    raise_operation_error(
                        get_request(),
                        "tenderPeriod should be extended by {0.days} days".format(self.tendering_period_extra)
                    )
                # self.update_date(after)  # There is a test that fails if uncomment
                # self.initialize_enquiry_period(after)
            self.invalidate_bids_data(after)
        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

    # helper methods
    @staticmethod
    def validate_fields_unchanged(before, after):
        # validate items cpv group
        cpv_group_lists = {i["classification"]["id"][:3] for i in before.get("items")}
        for item in after.get("items", ""):
            cpv_group_lists.add(item["classification"]["id"][:3])
        if len(cpv_group_lists) != 1:
            raise_operation_error(
                get_request(),
                "Can't change classification",
                name="item"
            )
        # it's serializible anyway
        # if before.get("enquiryPeriod") != after.get("enquiryPeriod"):
        #     raise_operation_error(
        #         get_request(),
        #         "Can't change enquiryPeriod",
        #         name="enquiryPeriod"
        #     )

    def invalidate_bids_data(self, tender):
        self.check_auction_time(tender)
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"

    @staticmethod
    def check_auction_time(tender):
        if check_auction_period(tender.get("auctionPeriod", {}), tender):
            del tender["auctionPeriod"]["startDate"]

        for lot in tender.get("lots", ""):
            if check_auction_period(lot.get("auctionPeriod", {}), tender):
                del lot["auctionPeriod"]["startDate"]

    # @staticmethod
    # def initialize_enquiry_period(tender):
    #     tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
    #     end_date = calculate_tender_business_date(tendering_end, -ENQUIRY_PERIOD_TIME, tender)
    #     clarifications_until = calculate_clarif_business_date(end_date, ENQUIRY_STAND_STILL_TIME, tender, True)
    #     enquiry_period = tender.get("enquiryPeriod")
    #     tender["enquiryPeriod"] = dict(
    #         startDate=tender["tenderPeriod"]["startDate"],
    #         endDate=end_date.isoformat(),
    #         clarificationsUntil=clarifications_until.isoformat(),
    #     )
    #     invalidation_date = enquiry_period and enquiry_period.get("invalidationDate")
    #     if invalidation_date:
    #         tender["enquiryPeriod"]["invalidationDate"] = invalidation_date

    @staticmethod
    def watch_value_meta_changes(tender):
        pass  # TODO: shouldn't it work here


class TenderDetailsState(CFAUATenderDetailsMixing, CFAUATenderState):
    pass
