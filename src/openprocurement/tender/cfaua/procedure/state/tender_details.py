from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.cfaua.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
    QUALIFICATION_COMPLAINT_STAND_STILL,
    PREQUALIFICATION_COMPLAINT_STAND_STILL,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.openua.procedure.state.tender_details import OpenUATenderDetailsMixing


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


class CFAUATenderDetailsMixing(OpenUATenderDetailsMixing):
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME

    set_object_status: callable  # from BaseState
    block_complaint_status: tuple  # from TenderState

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        self.initialize_enquiry_period(tender)

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
            self.invalidate_bids_data(after)
        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        if after["status"] in ("draft", "active.tendering"):
            self.initialize_enquiry_period(after)

        self.validate_tender_exclusion_criteria(before, after)
        self.validate_tender_language_criteria(before, after)
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

    def status_up(self, before, after, data):
        if (
            before == "draft" and after == "active.tendering"
            or before == "active.pre-qualification" and after == "active.pre-qualification.stand-still"
            or before == "active.qualification" and after == "active.qualification.stand-still"
        ):
            pass  # allowed scenario
        else:
            raise_operation_error(
                get_request(),
                f"Can't update tender to {after} status",
                status=403,
                location="body",
                name="status"
            )
        super().status_up(before, after, data)

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
        # it's serializible anyway
        # if before.get("enquiryPeriod") != after.get("enquiryPeriod"):
        #     raise_operation_error(
        #         get_request(),
        #         "Can't change enquiryPeriod",
        #         name="enquiryPeriod"
        #     )

    # def invalidate_bids_data(self, tender):
    #     tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
    #     for bid in tender.get("bids", ""):
    #         if bid.get("status") not in ("deleted", "draft"):
    #             bid["status"] = "invalid"

    @staticmethod
    def watch_value_meta_changes(tender):
        pass  # TODO: shouldn't it work here


class TenderDetailsState(CFAUATenderDetailsMixing, CFAUATenderState):
    pass
