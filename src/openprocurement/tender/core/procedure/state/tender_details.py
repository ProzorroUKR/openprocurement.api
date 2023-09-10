from datetime import timedelta
from typing import TYPE_CHECKING

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from openprocurement.tender.core.constants import (
    PROCUREMENT_METHOD_SELECTIVE,
    LIMITED_PROCUREMENT_METHOD_TYPES,
    PROCUREMENT_METHOD_LIMITED,
    PROCUREMENT_METHOD_OPEN,
    SELECTIVE_PROCUREMENT_METHOD_TYPES,
)
from openprocurement.tender.core.procedure.context import (
    get_request,
    get_tender_config,
)
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    set_mode_test_titles,
    tender_created_before,
    validate_field,
)
from openprocurement.api.utils import (
    raise_operation_error,
)
from openprocurement.api.constants import (
    RELEASE_ECRITERIA_ARTICLE_17,
    TENDER_PERIOD_START_DATE_STALE_MINUTES,
    TENDER_CONFIG_OPTIONALITY,
    TENDER_CONFIG_JSONSCHEMAS,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.utils import calculate_tender_business_date, calculate_complaint_business_date

if TYPE_CHECKING:
    baseclass = TenderState
else:
    baseclass = object


class TenderConfigMixin(baseclass):
    configurations = (
        "hasAuction",
        "hasAwardingOrder",
        "hasValueRestriction",
        "valueCurrencyEquality",
        "hasPrequalification",
        "minBidsNumber",
        "preSelection",
    )

    def validate_config(self, data):
        config = get_tender_config()
        for config_name in self.configurations:
            value = config.get(config_name)

            if value is None and TENDER_CONFIG_OPTIONALITY.get(config_name, True) is False:
                raise_operation_error(
                    self.request,
                    "This field is required.",
                    status=422,
                    location="body",
                    name=config_name,
                )

            procurement_method_type = data.get("procurementMethodType")
            config_schema = TENDER_CONFIG_JSONSCHEMAS.get(procurement_method_type)
            if not config_schema:
                raise NotImplementedError
            schema = config_schema["properties"][config_name]
            try:
                validate(value, schema)
            except ValidationError as e:
                raise_operation_error(
                    self.request,
                    e.message,
                    status=422,
                    location="body",
                    name=config_name,
                )


class TenderDetailsMixing(TenderConfigMixin, baseclass):
    """
    describes business logic rules for tender owners
    when they prepare tender for tendering stage
    """

    config: dict

    tender_create_accreditations = None
    tender_central_accreditations = None
    tender_edit_accreditations = None

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

    enquiry_period_timedelta: timedelta
    enquiry_stand_still_timedelta: timedelta
    allow_tender_period_start_date_change = False
    pre_qualification_complaint_stand_still = timedelta(days=0)
    tendering_period_extra_working_days = False

    def validate_tender_patch(self, before, after):
        request = get_request()
        if before["status"] != after["status"]:
            self.validate_cancellation_blocks(request, before)

    def on_post(self, tender):
        self.validate_config(tender)
        self.validate_procurement_method(tender)
        self.validate_minimal_step(tender)
        self.validate_submission_method(tender)
        self.watch_value_meta_changes(tender)
        self.update_date(tender)
        super().on_post(tender)

        # set author for documents passed with tender data
        for doc in tender.get("documents", ""):
            doc["author"] = "tender_owner"

    def set_mode_test(self, tender):
        config = get_tender_config()
        if config.get("test"):
            tender["mode"] = "test"
        if tender.get("mode") == "test":
            set_mode_test_titles(tender)

    def on_patch(self, before, after):
        self.validate_procurement_method(after, before=before)
        self.validate_pre_qualification_status_change(before, after)
        self.validate_tender_period_start_date_change(before, after)
        self.validate_minimal_step(after, before=before)
        self.validate_submission_method(after, before=before)
        self.validate_kind_change(after, before)
        self.validate_award_criteria_change(after, before)
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

    def validate_pre_qualification_status_change(self, before, after):
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

                if self.all_bids_are_reviewed(after):
                    after["qualificationPeriod"]["endDate"] = calculate_complaint_business_date(
                        get_now(), self.pre_qualification_complaint_stand_still, after
                    ).isoformat()
                    after["qualificationPeriod"]["reportingDatePublication"] = get_now().isoformat()
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

    @staticmethod
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

    @staticmethod
    def all_awards_are_reviewed(tender):
        """
        checks if all tender awards are reviewed
        """
        return all(award["status"] != "pending" for award in tender["awards"])

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

    def validate_tender_period_start_date_change(self, before, after):
        if self.allow_tender_period_start_date_change:
            return

        if "draft" in before["status"]:
            # draft, draft.stage2
            # still can change tenderPeriod.startDate
            return

        tender_period_start_before = before.get("tenderPeriod", {}).get("startDate")
        tender_period_start_after = after.get("tenderPeriod", {}).get("startDate")
        if tender_period_start_before != tender_period_start_after:
            raise_operation_error(
                get_request(),
                "Can't change tenderPeriod.startDate",
                status=422,
                location="body",
                name="tenderPeriod.startDate"
            )

    def validate_award_criteria_change(self, after, before):
        if before.get("awardCriteria") != after.get("awardCriteria"):
            raise_operation_error(
                get_request(),
                "Can't change awardCriteria",
                name="awardCriteria"
            )

    def validate_kind_change(self, after, before):
        if before["status"] not in ("draft", "draft.stage2"):
            if before["procuringEntity"].get("kind") != after["procuringEntity"].get("kind"):
                raise_operation_error(
                    get_request(),
                    "Can't change procuringEntity.kind in a public tender",
                    status=422,
                    location="body",
                    name="procuringEntity"
                )

    @classmethod
    def validate_tender_exclusion_criteria(cls, before, after):
        if tender_created_before(RELEASE_ECRITERIA_ARTICLE_17):
            return

        if after.get("status") not in ("active", "active.tendering"):
            return

        tender_criteria = {
            criterion["classification"]["id"]
            for criterion in after.get("criteria", "")
            if criterion.get("classification")
        }

        # exclusion criteria
        if cls.required_exclusion_criteria - tender_criteria:
            raise_operation_error(
                get_request(),
                f"Tender must contain all required `EXCLUSION` criteria: "
                f"{', '.join(sorted(cls.required_exclusion_criteria))}",
            )

    @staticmethod
    def validate_tender_language_criteria(before, after):
        if tender_created_before(RELEASE_ECRITERIA_ARTICLE_17):
            return

        if after.get("status") not in ("active", "active.tendering"):
            return

        tender_criteria = {
            criterion["classification"]["id"]
            for criterion in after.get("criteria", "")
            if criterion.get("classification")
        }
        language_criterion = "CRITERION.OTHER.BID.LANGUAGE"
        if language_criterion not in tender_criteria:
            raise_operation_error(get_request(), f"Tender must contain {language_criterion} criterion")

    def validate_minimal_step(self, data, before=None):
        config = get_tender_config()
        kwargs = {
            "before": before,
            "enabled": config.get("hasAuction") is True,
        }
        validate_field(data, "minimalStep", **kwargs)

    def validate_submission_method(self, data, before=None):
        config = get_tender_config()
        kwargs = {
            "before": before,
            "enabled": config.get("hasAuction") is True,
        }
        validate_field(data, "submissionMethod", default="electronicAuction", **kwargs)
        validate_field(data, "submissionMethodDetails", required=False, **kwargs)
        validate_field(data, "submissionMethodDetails_en", required=False, **kwargs)
        validate_field(data, "submissionMethodDetails_ru", required=False, **kwargs)

    @staticmethod
    def default_procurement_method(data):
        config = get_tender_config()
        if config["preSelection"] is True:
            return PROCUREMENT_METHOD_SELECTIVE
        if data["procurementMethodType"] in SELECTIVE_PROCUREMENT_METHOD_TYPES:
            return PROCUREMENT_METHOD_SELECTIVE
        if data["procurementMethodType"] in LIMITED_PROCUREMENT_METHOD_TYPES:
            return PROCUREMENT_METHOD_LIMITED
        return PROCUREMENT_METHOD_OPEN

    def validate_procurement_method(self, data, before=None):
        default_procurement_method = self.default_procurement_method(data)
        if before is None and data.get("procurementMethod") is None:
            # default on post only
            data["procurementMethod"] = default_procurement_method
        if data.get("procurementMethod") != default_procurement_method:
            raise_operation_error(
                self.request,
                "procurementMethod should be {}".format(default_procurement_method),
                status=422,
                location="body",
                name="procurementMethod",
            )

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

    def validate_tender_period_extension(self, tender):
        if "tenderPeriod" in tender and "endDate" in tender["tenderPeriod"]:
            tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
            if calculate_tender_business_date(get_now(), self.tendering_period_extra, tender) > tendering_end:
                raise_operation_error(
                    get_request(),
                    "tenderPeriod should be extended by {0.days} {1}".format(
                        self.tendering_period_extra,
                        "working days" if self.tendering_period_extra_working_days else "days",
                    )
                )


class TenderDetailsState(TenderDetailsMixing, TenderState):
    pass
