from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.open.procedure.state.tender import OpenTenderState
from openprocurement.tender.open.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
)
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
    calculate_clarif_business_date,
    check_auction_period,
)
from openprocurement.api.utils import raise_operation_error


class TenderDetailsState(TenderDetailsMixing, OpenTenderState):

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = False

    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME

    required_exclusion_criteria = {
        "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
        "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
        "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
        "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
        "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
        "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
        "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
        "CRITERION.EXCLUSION.NATIONAL.OTHER",
    }

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        self.initialize_enquiry_period(tender)

    def on_patch(self, before, after):
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

        self.validate_tender_exclusion_criteria(before, after)
        self.validate_tender_language_criteria(before, after)

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

        if after["status"] != "draft":
            for item in after["items"]:
                if not item.get("relatedLot"):
                    raise_operation_error(
                        get_request(),
                        "This field is required",
                        status=422,
                        location="body",
                        name="item.relatedLot"
                    )

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

        # bid invalidation rules
        if before["status"] == "active.tendering":
            self.validate_tender_period_extension(after)
            self.invalidate_bids_data(after)
        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        if after["status"] in ("draft", "active.tendering"):
            self.initialize_enquiry_period(after)

    def initialize_enquiry_period(self, tender):
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_tender_business_date(tendering_end, self.enquiry_period_timedelta, tender)
        clarifications_until = calculate_clarif_business_date(
            end_date, self.enquiry_stand_still_timedelta,  tender
        )
        enquiry_period = tender.get("enquiryPeriod")
        tender["enquiryPeriod"] = dict(
            startDate=tender["tenderPeriod"]["startDate"],
            endDate=end_date.isoformat(),
            clarificationsUntil=clarifications_until.isoformat(),
        )
        invalidation_date = enquiry_period and enquiry_period.get("invalidationDate")
        if invalidation_date:
            tender["enquiryPeriod"]["invalidationDate"] = invalidation_date

    def validate_tender_period_extension(self, tender):
        if "tenderPeriod" in tender and "endDate" in tender["tenderPeriod"]:
            # self.request.validated["tender"].tenderPeriod.import_data(data["tenderPeriod"])
            tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
            if calculate_tender_business_date(get_now(), self.tendering_period_extra, tender) > tendering_end:
                raise_operation_error(
                    get_request(),
                    "tenderPeriod should be extended by {0.days} {1}".format(
                        self.tendering_period_extra,
                        "working days" if self.tendering_period_extra_working_days else "days",
                    )
                )

    @classmethod
    def invalidate_bids_data(cls, tender):
        cls.check_auction_time(tender)
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
