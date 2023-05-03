from openprocurement.tender.core.procedure.context import get_request, \
    get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.openeu.constants import PREQUALIFICATION_COMPLAINT_STAND_STILL
from openprocurement.tender.openua.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    COMPLAINT_SUBMIT_TIME,
    ENQUIRY_STAND_STILL_TIME,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.openua.procedure.state.tender_details import OpenUATenderDetailsMixing


def all_bids_are_reviewed():
    tender = get_tender()
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


class OpenEUTenderDetailsMixing(OpenUATenderDetailsMixing):
    tendering_period_extra = TENDERING_EXTRA_PERIOD

    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        self.initialize_enquiry_period(tender)
        self.update_complaint_period(tender)

    def on_patch(self, before, after):
        if "draft" not in before["status"]:
            tendering_start = before.get("tenderPeriod", {}).get("startDate")
            if tendering_start != after.get("tenderPeriod", {}).get("startDate"):
                raise_operation_error(
                    get_request(),
                    "Can't change tenderPeriod.startDate",
                    status=422,
                    location="body",
                    name="tenderPeriod.startDate"
                )

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

                if all_bids_are_reviewed():
                    after["qualificationPeriod"]["endDate"] = calculate_complaint_business_date(
                        get_now(), PREQUALIFICATION_COMPLAINT_STAND_STILL, after
                    ).isoformat()
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
                self.update_complaint_period(after)
            self.invalidate_bids_data(after)

        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        if after["status"] in ("draft", "draft.stage2", "active.tendering"):
            self.initialize_enquiry_period(after)

        self.validate_tender_exclusion_criteria(before, after)
        self.validate_tender_language_criteria(before, after)
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

    # def invalidate_bids_data(self, tender):
    #     tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
    #     for bid in tender.get("bids", ""):
    #         if bid.get("status") not in ("deleted", "draft"):
    #             bid["status"] = "invalid"

    @staticmethod
    def update_complaint_period(tender):
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_complaint_business_date(tendering_end, -COMPLAINT_SUBMIT_TIME, tender).isoformat()
        tender["complaintPeriod"] = dict(startDate=tender["tenderPeriod"]["startDate"], endDate=end_date)


class TenderDetailsState(OpenEUTenderDetailsMixing, OpenEUTenderState):
    pass
