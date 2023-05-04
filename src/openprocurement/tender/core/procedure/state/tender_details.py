from openprocurement.tender.core.procedure.context import (
    get_request,
    get_tender_config,
)
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    set_mode_test_titles,
)
from openprocurement.api.utils import raise_operation_error, get_first_revision_date
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17, TENDER_PERIOD_START_DATE_STALE_MINUTES
from datetime import timedelta


class TenderDetailsMixing:
    config: dict

    # from tender base class
    validate_cancellation_blocks: callable

    required_exclusion_criteria = {
        "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
        "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
        "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
        "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
        "CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES",
        "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
        "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
        "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
        "CRITERION.EXCLUSION.NATIONAL.OTHER",
    }

    """
    describes business logic rules for tender owners
    when they prepare tender for tendering stage
    """
    def validate_tender_patch(self, before, after):
        request = get_request()
        if before["status"] != after["status"]:
            self.validate_cancellation_blocks(request, before)

    def on_post(self, tender):
        self.watch_value_meta_changes(tender)
        self.update_date(tender)
        super().on_post(tender)

    def set_mode_test(self, tender):
        config = get_tender_config()
        if config.get("test"):
            tender["mode"] = "test"
        if tender.get("mode") == "test":
            set_mode_test_titles(tender)

    def on_patch(self, before, after):
        if before["status"] not in ("draft", "draft.stage2"):
            if before["procuringEntity"]["kind"] != after["procuringEntity"]["kind"]:
                raise_operation_error(
                    get_request(),
                    "Can't change procuringEntity.kind in a public tender",
                    status=422,
                    location="body",
                    name="procuringEntity"
                )
        if before.get("awardCriteria") != after.get("awardCriteria"):
            raise_operation_error(
                get_request(),
                "Can't change awardCriteria",
                name="awardCriteria"
            )

        self.watch_value_meta_changes(after)
        super().on_patch(before, after)

    def always(self, data):
        self.set_mode_test(data)
        super().always(data)

    def status_up(self, before, after, data):
        if after == "draft" and before != "draft":
            raise_operation_error(
                get_request(),
                "Can't change status to draft",
                status=422,
                location="body",
                name="status"
            )
        elif after == "active.tendering" and before != "active.tendering":
            tendering_start = data["tenderPeriod"]["startDate"]
            if dt_from_iso(tendering_start) <= get_now() - timedelta(minutes=TENDER_PERIOD_START_DATE_STALE_MINUTES):
                raise_operation_error(
                    get_request(),
                    "tenderPeriod.startDate should be in greater than current date",
                    status=422,
                    location="body",
                    name="tenderPeriod.startDate"
                )
        super().status_up(before, after, data)

    @staticmethod
    def update_date(tender):
        now = get_now().isoformat()
        tender["date"] = now

        for lot in tender.get("lots", ""):
            lot["date"] = now

    @staticmethod
    def watch_value_meta_changes(tender):
        # tender currency and valueAddedTaxIncluded must be specified only ONCE
        # instead it's specified in many places but we need keep them the same
        value = tender.get("value")
        if not value:
            return
        currency = value.get("currency")
        tax_inc = value.get("valueAddedTaxIncluded")

        # items
        for item in tender["items"]:
            if "unit" in item and "value" in item["unit"]:
                item["unit"]["value"]["currency"] = currency
                item["unit"]["value"]["valueAddedTaxIncluded"] = tax_inc

        # lots
        for lot in tender.get("lots", ""):
            value = lot.get("value")
            if value:
                value["currency"] = currency
                value["valueAddedTaxIncluded"] = tax_inc

            minimal_step = lot.get("minimalStep")
            if minimal_step:
                minimal_step["currency"] = currency
                minimal_step["valueAddedTaxIncluded"] = tax_inc

    enquiry_period_timedelta: timedelta
    enquiry_stand_still_timedelta: timedelta

    @classmethod
    def validate_tender_exclusion_criteria(cls, before, after):
        if (
            get_first_revision_date(before, default=get_now()) < RELEASE_ECRITERIA_ARTICLE_17
            or after.get("status") not in ("active", "active.tendering")
        ):
            return

        tender_criteria = {criterion["classification"]["id"]
                           for criterion in after.get("criteria", "")
                           if criterion.get("classification")}

        # exclusion criteria
        if cls.required_exclusion_criteria - tender_criteria:
            raise_operation_error(
                get_request(),
                f"Tender must contain all required `EXCLUSION` criteria: "
                f"{', '.join(sorted(cls.required_exclusion_criteria))}",
            )

    @staticmethod
    def validate_tender_language_criteria(before, after):
        if (
            get_first_revision_date(before, default=get_now()) < RELEASE_ECRITERIA_ARTICLE_17
            or after.get("status") not in ("active", "active.tendering")
        ):
            return

        tender_criteria = {criterion["classification"]["id"]
                           for criterion in after.get("criteria", "")
                           if criterion.get("classification")}
        language_criterion = "CRITERION.OTHER.BID.LANGUAGE"
        if language_criterion not in tender_criteria:
            raise_operation_error(get_request(), f"Tender must contain {language_criterion} criterion")
