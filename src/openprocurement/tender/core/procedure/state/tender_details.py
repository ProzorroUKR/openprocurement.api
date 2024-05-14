from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from math import ceil, floor

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from openprocurement.api.constants import (
    CPV_PREFIX_LENGTH_TO_NAME,
    EVALUATION_REPORTS_DOC_REQUIRED_FROM,
    MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM,
    MILESTONES_VALIDATION_FROM,
    MINIMAL_STEP_VALIDATION_FROM,
    MINIMAL_STEP_VALIDATION_LOWER_LIMIT,
    MINIMAL_STEP_VALIDATION_PRESCISSION,
    MINIMAL_STEP_VALIDATION_UPPER_LIMIT,
    NOTICE_DOC_REQUIRED_FROM,
    RELATED_LOT_REQUIRED_FROM,
    RELEASE_ECRITERIA_ARTICLE_17,
    TENDER_CONFIG_JSONSCHEMAS,
    TENDER_CONFIG_OPTIONALITY,
    TENDER_PERIOD_START_DATE_STALE_MINUTES,
    WORKING_DAYS,
)
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_agreement, get_object, get_tender
from openprocurement.api.procedure.utils import (
    get_cpv_prefix_length,
    get_cpv_uniq_prefixes,
    to_decimal,
)
from openprocurement.api.utils import (
    get_first_revision_date,
    get_tender_category,
    get_tender_profile,
    raise_operation_error,
)
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.tender.core.constants import (
    AGREEMENT_CONTRACTS_MESSAGE,
    AGREEMENT_IDENTIFIER_MESSAGE,
    AGREEMENT_NOT_FOUND_MESSAGE,
    AGREEMENT_STATUS_MESSAGE,
    CRITERION_TECHNICAL_FEATURES,
    LIMITED_PROCUREMENT_METHOD_TYPES,
    PROCUREMENT_METHOD_LIMITED,
    PROCUREMENT_METHOD_OPEN,
    PROCUREMENT_METHOD_SELECTIVE,
    SELECTIVE_PROCUREMENT_METHOD_TYPES,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.criterion import ReqStatuses
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    set_mode_test_titles,
    tender_created_after,
    tender_created_before,
    validate_field,
)
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_doc_type_required,
)
from openprocurement.tender.core.utils import (
    calculate_complaint_business_date,
    calculate_tender_business_date,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    COMPETITIVE_ORDERING,
)
from openprocurement.tender.pricequotation.constants import PQ


class TenderConfigMixin:
    configurations = (
        "hasAuction",
        "hasAwardingOrder",
        "hasValueRestriction",
        "valueCurrencyEquality",
        "hasPrequalification",
        "minBidsNumber",
        "hasPreSelectionAgreement",
        "hasTenderComplaints",
        "hasAwardComplaints",
        "hasCancellationComplaints",
        "hasValueEstimation",
        "hasQualificationComplaints",
        "tenderComplainRegulation",
        "qualificationComplainDuration",
        "awardComplainDuration",
        "restricted",
        "cancellationComplainDuration",
    )

    def validate_config(self, data):
        for config_name in self.configurations:
            value = data["config"].get(config_name)

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

        self.validate_restricted_config(data)
        self.validate_estimated_value_config(data)

    def validate_estimated_value_config(self, data):
        if (
            data["procurementMethodType"] != "esco"
            and data["config"]["hasValueEstimation"] is False
            and data["config"]["hasValueRestriction"] is True
        ):
            raise_operation_error(
                self.request,
                "hasValueRestriction should be False",
                status=422,
                location="body",
                name="value",
            )

    def validate_restricted_config(self, data):
        has_restricted_preselection_agreement = False
        agreement = get_agreement()
        if agreement:
            has_restricted_preselection_agreement = agreement["config"]["restricted"] is True
        if has_restricted_preselection_agreement is True and data["config"]["restricted"] is False:
            raise_operation_error(
                self.request,
                "Value must be True.",
                status=422,
                location="body",
                name="restricted",
            )
        elif has_restricted_preselection_agreement is False and data["config"]["restricted"] is True:
            raise_operation_error(
                self.request,
                "Value must be False.",
                status=422,
                location="body",
                name="restricted",
            )


class TenderDetailsMixing(TenderConfigMixin):
    """
    describes business logic rules for tender owners
    when they prepare tender for tendering stage
    """

    config: dict

    tender_create_accreditations = None
    tender_central_accreditations = None
    tender_edit_accreditations = None

    required_criteria = ()

    enquiry_period_timedelta: timedelta
    enquiry_stand_still_timedelta: timedelta
    tendering_period_extra_working_days = False
    agreement_min_active_contracts = 3
    should_validate_cpv_prefix = True
    should_validate_pre_selection_agreement = True
    should_validate_notice_doc_required = False
    agreement_field = "agreements"
    should_validate_lot_minimal_step = True
    tender_complain_regulation_working_days = False

    calendar = WORKING_DAYS

    def validate_tender_patch(self, before, after):
        request = get_request()
        if before["status"] != after["status"]:
            self.validate_cancellation_blocks(request, before)

    def on_post(self, tender):
        self.validate_config(tender)
        self.validate_procurement_method(tender)
        self.validate_lots_count(tender)
        self.validate_tender_value(tender)
        self.validate_tender_lots(tender)
        self.validate_milestones(tender)
        self.validate_minimal_step(tender)
        self.validate_submission_method(tender)
        self.validate_items_classification_prefix(tender)
        self.validate_docs(tender)
        self.watch_value_meta_changes(tender)
        self.update_complaint_period(tender)
        self.update_date(tender)
        self.validate_change_item_profile_or_category(tender, {})
        super().on_post(tender)

        # set author for documents passed with tender data
        for doc in tender.get("documents", ""):
            doc["author"] = "tender_owner"

    def on_patch(self, before, after):
        self.validate_procurement_method(after, before=before)
        self.validate_lots_count(after)
        self.validate_milestones(after)
        self.validate_pre_qualification_status_change(before, after)
        self.validate_tender_period_start_date_change(before, after)
        self.validate_minimal_step(after, before=before)
        self.validate_tender_value(after)
        self.validate_tender_lots(after, before=before)
        self.validate_submission_method(after, before=before)
        self.validate_kind_change(after, before)
        self.validate_award_criteria_change(after, before)
        self.validate_items_classification_prefix(after)
        self.validate_action_with_exist_inspector_review_request(("tenderPeriod",))
        self.validate_docs(after, before)
        self.update_complaint_period(after)
        self.watch_value_meta_changes(after)
        self.validate_required_criteria(before, after)
        self.invalidate_review_requests()
        self.validate_remove_inspector(before, after)
        self.validate_change_item_profile_or_category(after, before)
        super().on_patch(before, after)

    def always(self, data):
        self.set_mode_test(data)
        super().always(data)

    def status_up(self, before, after, data):
        if after == "draft" and before != "draft":
            raise_operation_error(
                get_request(), "Can't change status to draft", status=422, location="body", name="status"
            )
        if after != "draft" and before == "draft":
            self.validate_pre_selection_agreement(data)
            self.validate_notice_doc_required(data)
        elif after == "active.tendering" and before != "active.tendering":
            tendering_start = data["tenderPeriod"]["startDate"]
            if dt_from_iso(tendering_start) <= get_now() - timedelta(minutes=TENDER_PERIOD_START_DATE_STALE_MINUTES):
                raise_operation_error(
                    get_request(),
                    "tenderPeriod.startDate should be in greater than current date",
                    status=422,
                    location="body",
                    name="tenderPeriod.startDate",
                )
        super().status_up(before, after, data)

    def validate_notice_doc_required(self, tender):
        if self.should_validate_notice_doc_required is False or not tender_created_after(NOTICE_DOC_REQUIRED_FROM):
            return
        validate_doc_type_required(tender.get("documents", []), document_of="tender")
        tender["noticePublicationDate"] = get_now().isoformat()

    def validate_pre_selection_agreement(self, tender):
        if self.should_validate_pre_selection_agreement is False:
            return

        def raise_agreements_error(message):
            raise_operation_error(
                self.request,
                message,
                status=422,
                location="body",
                name=self.agreement_field,
            )

        if tender["config"]["hasPreSelectionAgreement"] is True:
            agreements = [tender["agreement"]] if tender.get("agreement") else tender.get("agreements")
            if not agreements:
                raise_agreements_error("This field is required.")

            if len(agreements) != 1:
                raise_agreements_error("Exactly one agreement is expected.")

            agreement = get_object("agreement")

            if not agreement:
                raise_agreements_error(AGREEMENT_NOT_FOUND_MESSAGE)

            tender_agreement_type_mapping = {
                COMPETITIVE_ORDERING: DPS_TYPE,
                PQ: ELECTRONIC_CATALOGUE_TYPE,
            }

            if tender_agreement_type_mapping[tender["procurementMethodType"]] != agreement["agreementType"]:
                raise_agreements_error("Agreement type mismatch.")

            if self.is_agreement_not_active(agreement):
                raise_agreements_error(AGREEMENT_STATUS_MESSAGE)

            if self.has_insufficient_active_contracts(agreement):
                raise_agreements_error(AGREEMENT_CONTRACTS_MESSAGE.format(self.agreement_min_active_contracts))

            if self.has_mismatched_procuring_entities(tender, agreement):
                raise_agreements_error(AGREEMENT_IDENTIFIER_MESSAGE)

    def set_mode_test(self, tender):
        if tender["config"].get("test"):
            tender["mode"] = "test"
        if tender.get("mode") == "test":
            set_mode_test_titles(tender)

    def validate_milestones(self, tender):
        grouped_data = defaultdict(list)
        sums = {
            "financing": defaultdict(Decimal),
            "delivery": defaultdict(Decimal),
        }
        related_lot_exists = False
        for milestone in tender.get("milestones", []):
            if milestone.get("type") == "financing":
                if (
                    get_first_revision_date(tender, default=get_now()) > MILESTONES_VALIDATION_FROM
                    and milestone.get("duration", {}).get("days", 0) > 1000
                ):
                    raise_operation_error(
                        get_request(),
                        [{"duration": ["days shouldn't be more than 1000 for financing milestone"]}],
                        status=422,
                        name="milestones",
                    )
            sums[milestone["type"]][milestone.get("relatedLot")] += to_decimal(milestone.get("percentage", 0))
            grouped_data[milestone.get('relatedLot')].append(milestone)

            if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM) and milestone.get('relatedLot'):
                related_lot_exists = True

        if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM):
            for lot, milestones in grouped_data.items():
                for i, milestone in enumerate(milestones):
                    if related_lot_exists and not milestone.get('relatedLot'):
                        raise_operation_error(
                            get_request(),
                            [
                                {
                                    "relatedLot": "Related lot must be set in all milestones or all milestones should be related to tender"
                                }
                            ],
                            status=422,
                            name="milestones",
                        )
                    if milestone.get("sequenceNumber") != i + 1:
                        raise_operation_error(
                            get_request(),
                            [
                                {
                                    "sequenceNumber": "Field should contain incrementing sequence numbers starting from 1 for tender/lot separately"
                                }
                            ],
                            status=422,
                            name="milestones",
                        )
        for milestone_type, values in sums.items():
            for uid, sum_value in values.items():
                if sum_value != Decimal("100"):
                    raise_operation_error(
                        get_request(),
                        f"Sum of the {milestone_type} milestone percentages {sum_value} "
                        f"is not equal 100{f' for lot {uid}' if uid else ''}.",
                        status=422,
                        name="milestones",
                    )

    def validate_lots_count(self, tender):
        tender = get_tender()
        if tender.get("procurementMethodType") == COMPETITIVE_ORDERING:
            # TODO: consider using config
            max_lots_count = 1
            if len(tender.get("lots", "")) > max_lots_count:
                raise_operation_error(
                    get_request(),
                    "Can't create more than {} lots".format(max_lots_count),
                    status=422,
                    location="body",
                    name="lots",
                )

    def validate_tender_lots(self, tender: dict, before=None) -> None:
        """Validate tender lots

        Validation includes lot value and lot minimal step, if required.

        :param tender: Tender dictionary.
        :param before: Tender dictionary before patch, optional
        :return: None
        """
        lots = tender.get("lots")

        if lots:
            lots_amounts = [lot.get("value").get("amount") for lot in lots if lot.get("value")]
            if tender["config"]["hasValueEstimation"] is False and any(lots_amounts):
                raise_operation_error(
                    self.request,
                    "Value amount should not be passed if tender does not have estimated value",
                    status=422,
                    location="body",
                    name="lots.value.amount",
                )

            for lot in lots:
                self.validate_minimal_step(lot, before)
                self.validate_lot_value(tender, lot)

    def validate_lot_value(self, tender: dict, lot: dict) -> None:
        """Validate lot value.

        Validation includes lot value and lot minimal step, if required.

        :param tender: Tender dictionary
        :param lot: Lot dictionary
        :return: None
        """
        has_value_estimation = tender["config"]["hasValueEstimation"]
        lot_value = lot.get("value", {})

        if not lot_value:
            return

        lot_min_step = lot.get("minimalStep", {})
        lot_value_amount = lot_value.get("amount")
        if has_value_estimation is True and lot_value_amount is None:
            raise_operation_error(
                self.request,
                "This field is required",
                status=422,
                name="lots.value.amount",
            )

        if has_value_estimation is False and lot_value_amount:
            raise_operation_error(
                self.request,
                "Rogue field",
                status=422,
                name="lots.value.amount",
            )

        lot_min_step_amount = lot_min_step.get("amount")

        if lot_min_step_amount is None:
            return

        if has_value_estimation and lot_value_amount is not None and lot_value_amount < lot_min_step_amount:
            raise_operation_error(
                self.request, "Minimal step value should be less than lot value", status=422, name="lots"
            )
        if self.should_validate_lot_minimal_step and has_value_estimation and lot_value_amount is not None:
            self.validate_minimal_step_limits(tender, lot_value_amount, lot_min_step_amount)

    def validate_minimal_step_limits(self, tender: dict, value_amount: float, minimal_step_amount: float) -> None:
        """Validate minimal step lower and upper limits.

        :param request: Request instance
        :param tender: Tender dictionary
        :param value_amount: Value amount
        :param minimal_step_amount: Minimal step amount
        :return: None
        """
        tender_created = get_first_revision_date(tender, default=get_now())
        if tender_created > MINIMAL_STEP_VALIDATION_FROM:
            precision_multiplier = 10**MINIMAL_STEP_VALIDATION_PRESCISSION

            lower_step = (
                floor(float(value_amount) * MINIMAL_STEP_VALIDATION_LOWER_LIMIT * precision_multiplier)
                / precision_multiplier
            )

            higher_step = (
                ceil(float(value_amount) * MINIMAL_STEP_VALIDATION_UPPER_LIMIT * precision_multiplier)
                / precision_multiplier
            )

            if higher_step < minimal_step_amount or minimal_step_amount < lower_step:
                raise_operation_error(
                    self.request,
                    "Minimal step value must be between 0.5% and 3% of value (with 2 digits precision).",
                    status=422,
                )

    def validate_pre_qualification_status_change(self, before, after):
        tender = get_tender()
        qualif_complain_duration = tender["config"]["qualificationComplainDuration"]

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
                        "Can't switch to 'active.pre-qualification.stand-still' before resolve all complaints",
                    )

                if tender_created_after(EVALUATION_REPORTS_DOC_REQUIRED_FROM):
                    validate_doc_type_required(
                        get_tender().get("documents", []),
                        document_type="evaluationReports",
                        document_of="tender",
                        after_date=get_tender()["qualificationPeriod"].get("reportingDatePublication"),
                    )
                if self.all_bids_are_reviewed(after):
                    end_date = calculate_complaint_business_date(
                        get_now(), timedelta(days=qualif_complain_duration), after
                    ).isoformat()

                    if qualif_complain_duration > 0:
                        for qualification in after["qualifications"]:
                            if qualification.get("status") in ["unsuccessful", "active"]:
                                qualification["complaintPeriod"] = {
                                    "startDate": get_now().isoformat(),
                                    "endDate": end_date,
                                }

                    after["qualificationPeriod"]["endDate"] = end_date
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
        if before["status"] in ("draft", "draft.stage2", "active.enquiries"):
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
                name="tenderPeriod.startDate",
            )

    def validate_award_criteria_change(self, after, before):
        if before.get("awardCriteria") != after.get("awardCriteria"):
            raise_operation_error(get_request(), "Can't change awardCriteria", name="awardCriteria")

    def validate_kind_change(self, after, before):
        if before["status"] not in ("draft", "draft.stage2"):
            if before["procuringEntity"].get("kind") != after["procuringEntity"].get("kind"):
                raise_operation_error(
                    get_request(),
                    "Can't change procuringEntity.kind in a public tender",
                    status=422,
                    location="body",
                    name="procuringEntity",
                )

    @classmethod
    def validate_required_criteria(cls, before, after):
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
        if set(cls.required_criteria) - tender_criteria:
            raise_operation_error(
                get_request(),
                f"Tender must contain all required criteria: {', '.join(sorted(cls.required_criteria))}",
            )

    def validate_minimal_step(self, data, before=None):
        """
        Minimal step validation.
        Minimal step should be required if tender has auction

        :param data: tender or lot
        :param before: tender or lot
        :return:
        """
        tender = get_tender()
        kwargs = {
            "before": before,
            "enabled": tender["config"]["hasAuction"] is True,
        }
        validate_field(data, "minimalStep", **kwargs)

    def validate_tender_value(self, tender):
        """Validate tender value.

        Validation includes tender value and tender minimal step, if required.

        :param tender: Tender dictionary
        :return: None
        """
        has_value_estimation = tender["config"]["hasValueEstimation"]
        tender_value = tender.get("value", {})
        if not tender_value:
            return

        tender_min_step = tender.get("minimalStep", {})
        tender_value_amount = tender_value.get("amount")
        if has_value_estimation is True and tender_value_amount is None:
            raise_operation_error(
                self.request,
                "This field is required",
                status=422,
                location="body",
                name="value.amount",
            )

        if has_value_estimation is False and tender_value_amount:
            raise_operation_error(
                self.request,
                "Rogue field",
                status=422,
                location="body",
                name="value.amount",
            )

        if tender_min_step and tender_value["currency"] != tender_min_step["currency"]:
            raise_operation_error(
                get_request(),
                "Tender minimal step currency should be identical to tender currency",
                status=422,
                location="body",
                name="minimalStep.currency",
            )

        if tender_min_step and tender_value["valueAddedTaxIncluded"] != tender_min_step["valueAddedTaxIncluded"]:
            raise_operation_error(
                get_request(),
                "Tender minimal step valueAddedTaxIncluded should be identical to tender valueAddedTaxIncluded",
                status=422,
                location="body",
                name="minimalStep.valueAddedTaxIncluded",
            )

        tender_min_step_amount = tender_min_step.get("amount")

        if tender_min_step_amount is None:
            return

        if has_value_estimation and tender_value_amount is not None and tender_value_amount < tender_min_step_amount:
            raise_operation_error(
                get_request(),
                "Tender minimal step amount should be less than tender amount",
                status=422,
                location="body",
                name="minimalStep.amount",
            )
        if has_value_estimation and tender_value_amount is not None:
            self.validate_minimal_step_limits(tender, tender_value_amount, tender_min_step_amount)

    def validate_submission_method(self, data, before=None):
        kwargs = {
            "before": before,
            "enabled": data["config"]["hasAuction"] is True,
        }
        validate_field(data, "submissionMethod", default="electronicAuction", **kwargs)
        validate_field(data, "submissionMethodDetails", required=False, **kwargs)
        validate_field(data, "submissionMethodDetails_en", required=False, **kwargs)
        validate_field(data, "submissionMethodDetails_ru", required=False, **kwargs)

    @staticmethod
    def default_procurement_method(data):
        if data["config"]["hasPreSelectionAgreement"] is True:
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

    def validate_items_classification_prefix(self, tender):
        if not self.should_validate_cpv_prefix:
            return

        # tender.items.classification
        classifications = [item["classification"] for item in tender.get("items", "")]

        prefix_length = get_cpv_prefix_length(classifications)
        prefix_name = CPV_PREFIX_LENGTH_TO_NAME[prefix_length]
        if len(get_cpv_uniq_prefixes(classifications, prefix_length)) != 1:
            raise_operation_error(
                get_request(), [f"CPV {prefix_name} of items should be identical"], status=422, name="items"
            )

        if not self.should_validate_pre_selection_agreement:
            return

        agreements = tender.get("agreements")

        if not agreements:
            return

        agreement = get_object("agreement")

        if not agreement:
            return

        # tender.items.classification + agreement.classification
        classifications.append(agreement["classification"])

        prefix_length = get_cpv_prefix_length(classifications)
        prefix_name = CPV_PREFIX_LENGTH_TO_NAME[prefix_length]
        if len(get_cpv_uniq_prefixes(classifications, prefix_length)) != 1:
            raise_operation_error(
                get_request(),
                [f"CPV {prefix_name} of items should be identical to agreement cpv"],
                status=422,
                name="items",
            )

    @classmethod
    def validate_items_classification_prefix_unchanged(cls, before, after):
        prefix_list = set()
        prefix_length = 3  # group
        for item in before.get("items", ""):
            prefix_list.add(item["classification"]["id"][:prefix_length])
        for item in after.get("items", ""):
            prefix_list.add(item["classification"]["id"][:prefix_length])
        if len(prefix_list) != 1:
            prefix_name = CPV_PREFIX_LENGTH_TO_NAME[prefix_length]
            raise_operation_error(
                get_request(), [f"Can't change classification {prefix_name} of items"], status=422, name="items"
            )

    def validate_tender_period_extension(self, tender):
        if "tenderPeriod" in tender and "endDate" in tender["tenderPeriod"]:
            tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
            if (
                calculate_tender_business_date(
                    get_now(),
                    self.tendering_period_extra,
                    tender=tender,
                    working_days=self.tendering_period_extra_working_days,
                )
                > tendering_end
            ):
                raise_operation_error(
                    get_request(),
                    "tenderPeriod should be extended by {0.days} {1}".format(
                        self.tendering_period_extra,
                        "working days" if self.tendering_period_extra_working_days else "days",
                    ),
                )

    def validate_docs(self, data, before=None):
        documents = data.get("documents", [])
        if before and len(before.get("documents", [])) != len(documents) or before is None:
            if tender_created_after(NOTICE_DOC_REQUIRED_FROM):
                validate_doc_type_quantity(documents)
            if tender_created_after(EVALUATION_REPORTS_DOC_REQUIRED_FROM):
                validate_doc_type_quantity(documents, document_type="evaluationReports")

    @staticmethod
    def calculate_item_identification_tuple(item):
        result = (
            item["id"],
            item["classification"]["id"],
            item["classification"]["scheme"],
            item["unit"]["code"] if item.get("unit") else None,
            tuple((c["id"], c["scheme"]) for c in item.get("additionalClassifications", "")),
        )
        return result

    @classmethod
    def is_agreement_not_active(cls, agreement):
        return agreement.get("status") != "active"

    @classmethod
    def has_insufficient_active_contracts(cls, agreement):
        active_contracts_count = sum(c["status"] == "active" for c in agreement.get("contracts", ""))
        return active_contracts_count < cls.agreement_min_active_contracts

    @classmethod
    def has_mismatched_procuring_entities(cls, tender, agreement):
        agreement_identifier = agreement["procuringEntity"]["identifier"]
        tender_identifier = tender["procuringEntity"]["identifier"]
        return (
            tender_identifier["id"] != agreement_identifier["id"]
            or tender_identifier["scheme"] != agreement_identifier["scheme"]
        )

    def validate_related_lot_in_items(self, after):
        if (
            tender_created_after(RELATED_LOT_REQUIRED_FROM)
            or after.get("procurementMethodType") in ABOVE_THRESHOLD_GROUP
        ) and after["status"] != "draft":
            for item in after["items"]:
                if not item.get("relatedLot"):
                    raise_operation_error(
                        get_request(), "This field is required", status=422, location="body", name="item.relatedLot"
                    )

    def update_complaint_period(self, tender):
        if tender["config"]["hasTenderComplaints"] is not True:
            return
        if "tenderPeriod" not in tender or "endDate" not in tender["tenderPeriod"]:
            return
        if tender["config"]["tenderComplainRegulation"] == 0:
            return
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_complaint_business_date(
            tendering_end,
            -timedelta(days=tender["config"]["tenderComplainRegulation"]),
            tender,
            working_days=self.tender_complain_regulation_working_days,
        )
        tender["complaintPeriod"] = {
            "startDate": tender["tenderPeriod"]["startDate"],
            "endDate": end_date.isoformat(),
        }

    def validate_remove_inspector(self, before, after):
        if after["status"] == "draft":
            return
        if before.get("inspector") and not after.get("inspector"):
            raise_operation_error(
                get_request(),
                f"You can't remove inspector in current({after['status']}) tender status",
                status=422,
            )

    def validate_change_item_profile_or_category(self, after: dict, before: dict) -> None:
        after_cp = {
            i["id"]: {"profile": i.get("profile"), "category": i.get("category")} for i in after.get("items", "")
        }
        before_cp = {
            i["id"]: {"profile": i.get("profile"), "category": i.get("category")} for i in before.get("items", "")
        }

        request = get_request()

        for k, after_values in after_cp.items():
            before_values = before_cp.get(k, {})
            if (before_values.get("profile") != after_values.get("profile")) or (
                before_values.get("category") != after_values.get("category")
            ):
                category_id = after_values.get("category")
                get_tender_category(request, category_id, ("active",))
                profile = get_tender_profile(request, after_values.get("profile"), ("active", "general"))
                if profile.get("relatedCategory") != category_id:
                    raise_operation_error(request, "Profile should be related to category", status=422)

                if before:
                    self.cancel_all_technical_criteria(after, k)

    def cancel_all_technical_criteria(self, tender: dict, item_id: str) -> None:
        for criterion in tender.get("criteria", ""):
            if (
                criterion.get("classification", {}).get("id") == CRITERION_TECHNICAL_FEATURES
                and criterion.get("relatedItem") == item_id
            ):
                for rg in criterion.get("requirementGroups", ""):
                    for req in rg.get("requirements", ""):
                        req["status"] = ReqStatuses.CANCELLED


class TenderDetailsState(TenderDetailsMixing, TenderState):
    pass
