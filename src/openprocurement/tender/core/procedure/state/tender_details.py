from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
from math import ceil, floor

from openprocurement.api.constants import (
    CPV_GROUP_PREFIX_LENGTH,
    CPV_PREFIX_LENGTH_TO_NAME,
    MINIMAL_STEP_VALIDATION_LOWER_LIMIT,
    MINIMAL_STEP_VALIDATION_PRESCISSION,
    MINIMAL_STEP_VALIDATION_UPPER_LIMIT,
    PROFILE_REQUIRED_MIN_VALUE_AMOUNT,
    TENDER_CONFIG_JSONSCHEMAS,
    TENDER_PERIOD_START_DATE_STALE_MINUTES,
    WORKING_DAYS,
)
from openprocurement.api.constants_env import (
    CRITERIA_CLASSIFICATION_UNIQ_FROM,
    EVALUATION_REPORTS_DOC_REQUIRED_FROM,
    MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM,
    MILESTONES_VALIDATION_FROM,
    MINIMAL_STEP_VALIDATION_FROM,
    NOTICE_DOC_REQUIRED_FROM,
    RELATED_LOT_REQUIRED_FROM,
    TENDER_CONFIG_OPTIONALITY,
)
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_agreement, get_object, get_tender
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.api.procedure.state.base import ConfigMixin
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.procedure.validation import (
    validate_items_classifications_prefixes,
)
from openprocurement.api.utils import (
    get_first_revision_date,
    get_tender_category,
    get_tender_profile,
    raise_operation_error,
)
from openprocurement.framework.ifi.constants import IFI_TYPE
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.constants import (
    AGREEMENT_CONTRACTS_MESSAGE,
    AGREEMENT_IDENTIFIER_MESSAGE,
    AGREEMENT_NOT_FOUND_MESSAGE,
    AGREEMENT_STATUS_MESSAGE,
    CRITERION_LOCALIZATION,
    CRITERION_TECHNICAL_FEATURES,
    LIMITED_PROCUREMENT_METHOD_TYPES,
    PROCUREMENT_METHOD_LIMITED,
    PROCUREMENT_METHOD_OPEN,
    PROCUREMENT_METHOD_SELECTIVE,
    SELECTIVE_PROCUREMENT_METHOD_TYPES,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.criterion import ReqStatuses
from openprocurement.tender.core.procedure.models.tender_base import (
    MainProcurementCategory,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    get_contract_template_names_for_classification_ids,
    set_mode_test_titles,
    tender_created_after,
    validate_field,
)
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_doc_type_required,
    validate_edrpou_confidentiality_doc,
)
from openprocurement.tender.core.utils import (
    calculate_tender_full_date,
    get_criteria_rules,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


class TenderConfigMixin(ConfigMixin):
    def get_config_schema(self, data):
        procurement_method_type = data.get("procurementMethodType")
        config_schema = TENDER_CONFIG_JSONSCHEMAS.get(procurement_method_type)

        if not config_schema:
            # procurementMethodType not found in TENDER_CONFIG_JSONSCHEMAS
            raise NotImplementedError

        config_schema = deepcopy(config_schema)

        return config_schema

    def validate_config(self, data):
        # load schema from standards
        config_schema = self.get_config_schema(data)

        # we will validate required fields manually
        config_schema.pop("required", None)

        # validate required fields
        properties = config_schema.get("properties", {})
        for config_name in properties.keys():
            value = data["config"].get(config_name)
            if value is None and TENDER_CONFIG_OPTIONALITY.get(config_name, True) is False:
                raise_operation_error(
                    self.request,
                    "This field is required.",
                    status=422,
                    location="body",
                    name=f"config.{config_name}",
                )

        # validate config with schema
        super().validate_config(data)

    def on_post(self, data):
        self.validate_config(data)
        self.validate_restricted_config(data)
        self.validate_estimated_value_config(data)
        self.validate_value_currency_equality(data)
        super().on_post(data)

    def validate_value_currency_equality(self, data):
        """Validate valueCurrencyEquality config option"""
        config = data["config"]
        value = config.get("valueCurrencyEquality")

        if value is False and any(
            [
                config.get("hasAuction"),
                config.get("hasAwardingOrder"),
                config.get("hasValueRestriction"),
            ]
        ):
            raise_operation_error(
                self.request,
                [
                    "valueCurrencyEquality can be False only if "
                    "hasAuction=False and "
                    "hasAwardingOrder=False and "
                    "hasValueRestriction=False"
                ],
                status=422,
                location="body",
                name="config.valueCurrencyEquality",
            )

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
                name="config.hasValueRestriction",
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
                name="config.restricted",
            )
        elif has_restricted_preselection_agreement is False and data["config"]["restricted"] is True:
            raise_operation_error(
                self.request,
                "Value must be False.",
                status=422,
                location="body",
                name="config.restricted",
            )


class BaseTenderDetailsMixing:
    """
    describes business logic rules for tender owners
    when they prepare tender for tendering stage
    """

    tender_create_accreditations = None
    tender_central_accreditations = None
    tender_edit_accreditations = None
    should_initialize_enquiry_period = True
    tender_period_working_day = True
    clarification_period_working_day = True
    enquiry_period_timedelta: timedelta
    tendering_period_extra_working_days = False
    agreement_min_active_contracts = 3
    should_validate_cpv_prefix = True
    should_validate_pre_selection_agreement = True
    should_validate_profiles_agreement_id = False
    should_match_agreement_procuring_entity = True
    should_validate_notice_doc_required = False
    agreement_field = "agreements"
    should_validate_lot_minimal_step = True
    tender_complain_regulation_working_days = False
    enquiry_before_tendering = False
    should_validate_related_lot_in_items = True
    agreement_allowed_types = [IFI_TYPE]
    agreement_with_items_forbidden = False
    agreement_without_items_forbidden = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    items_profile_required = False

    calendar = WORKING_DAYS

    def validate_tender_patch(self, before, after):
        request = get_request()
        if before["status"] != after["status"]:
            self.validate_cancellation_blocks(request, before)

    def on_post(self, tender):
        self.validate_procurement_method(tender)
        self.validate_tender_value(tender)
        self.validate_tender_lots(tender)
        self.validate_milestones(tender)
        self.validate_minimal_step(tender)
        self.validate_submission_method(tender)
        self.validate_items_classification_prefix(tender)
        self.validate_pre_selection_agreement(tender)
        self.validate_items_with_agreement(tender)
        self.validate_docs(tender)
        self.watch_value_meta_changes(tender)
        self.initialize_enquiry_period(tender)
        self.update_complaint_period(tender)
        self.update_date(tender)
        self.validate_change_item_profile_or_category(tender, {})
        self.validate_contract_template_name(tender, {})
        self.validate_criteria_requirements_rules(tender.get("criteria", []))
        super().on_post(tender)

        # set author for documents passed with tender data
        for doc in tender.get("documents", ""):
            doc["author"] = "tender_owner"

    def on_patch(self, before, after):
        enquire_start = before.get("enquiryPeriod", {}).get("startDate")
        if enquire_start and not after.get("enquiryPeriod", {}).get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="enquiryPeriod",
            )

        tendering_start = before.get("tenderPeriod", {}).get("startDate")
        if tendering_start and not after.get("tenderPeriod", {}).get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="tenderPeriod",
            )

        # bid invalidation rules
        if before["status"] == "active.tendering":
            self.validate_tender_period_extension(after)
            self.invalidate_bids_data(after)
        elif after["status"] == "active.tendering":
            self.set_enquiry_period_invalidation_date(after)

        self.validate_contract_template_name(after, before=before)
        self.validate_procurement_method(after, before=before)
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
        self.validate_pre_selection_agreement(after)
        self.validate_items_with_agreement(after)
        self.validate_action_with_exist_inspector_review_request(("tenderPeriod",))
        self.validate_docs(after, before)
        self.update_complaint_period(after)
        self.watch_value_meta_changes(after)
        self.validate_required_criteria(before, after)
        if tender_created_after(CRITERIA_CLASSIFICATION_UNIQ_FROM):
            self._validate_criterion_uniq(after.get("criteria", []))
        if before.get("criteria") != after.get("criteria"):
            self.validate_criteria_requirements_rules(after.get("criteria", []))
        self.invalidate_review_requests()
        self.validate_remove_inspector(before, after)
        if after["status"] in ("draft", "draft.stage2", "active.enquiries", "active.tendering"):
            self.initialize_enquiry_period(after)

        if self.should_validate_related_lot_in_items:
            self.validate_related_lot_in_items(after)

        if after["status"] != "draft" and before["status"] == "draft":
            self.validate_pre_selection_agreement_on_activation(after)
            self.validate_profiles_agreement_id(after)
            self.validate_change_item_profile_or_category(after, before, force_validate=True)
            self.validate_notice_doc_required(after)
            self.validate_criteria_requirement_from_market(after.get("criteria", []))
        else:
            self.validate_change_item_profile_or_category(after, before)

        super().on_patch(before, after)

    def always(self, data):
        self.validate_items_profile(data)
        self.set_mode_test(data)
        super().always(data)

    def status_up(self, before, after, data):
        if after == "draft" and before != "draft":
            raise_operation_error(
                get_request(),
                "Can't change status to draft",
                status=422,
                location="body",
                name="status",
            )
        if after == "active.tendering" and before != "active.tendering":
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

    def get_tender_agreements(self, tender):
        tender_agreements = tender.get(self.agreement_field)
        if not tender_agreements:
            return []

        if not isinstance(tender_agreements, list):
            # PQ has field "agreement" with single object instead of "agreements" with list of objects
            tender_agreements = [tender_agreements]

        return tender_agreements

    def validate_pre_selection_agreement(self, tender):
        if self.should_validate_pre_selection_agreement is False:
            return

        tender_agreements = self.get_tender_agreements(tender)

        if tender["config"]["hasPreSelectionAgreement"] is False:
            if tender_agreements:
                message = "Agreements cannot be specified when 'hasPreSelectionAgreement' is False."
                raise_operation_error(self.request, message, status=422, name=self.agreement_field)
            return

        if not tender_agreements:
            message = "This field is required."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if len(tender_agreements) != 1:
            message = "Exactly one agreement is expected."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        agreement = get_object("agreement")

        if not agreement:
            message = AGREEMENT_NOT_FOUND_MESSAGE
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if agreement["agreementType"] not in self.agreement_allowed_types:
            message = "Agreement type mismatch."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.agreement_with_items_forbidden and agreement.get("items"):
            message = "Agreement with items is not allowed."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.agreement_without_items_forbidden and not agreement.get("items"):
            message = "Agreement without items is not allowed."
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.has_mismatched_procuring_entities(tender, agreement):
            message = AGREEMENT_IDENTIFIER_MESSAGE
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

    def validate_pre_selection_agreement_on_activation(self, tender):
        """
        Validations of agreement on activation
        We dont care if agreement was changed after tender was activated
        and those valdations no longer pass
        """
        if self.should_validate_pre_selection_agreement is False:
            return

        if tender["config"]["hasPreSelectionAgreement"] is False:
            return

        agreement = get_object("agreement")

        if self.is_agreement_not_active(agreement):
            message = AGREEMENT_STATUS_MESSAGE
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

        if self.has_insufficient_active_contracts(agreement):
            message = AGREEMENT_CONTRACTS_MESSAGE.format(self.agreement_min_active_contracts)
            raise_operation_error(self.request, message, status=422, name=self.agreement_field)

    def validate_profiles_agreement_id(self, tender):
        if self.should_validate_profiles_agreement_id is False:
            return

        profile_ids = []

        tender_agreements = self.get_tender_agreements(tender)

        if not tender_agreements:
            return

        for items in tender.get("items", []):
            profile_id = items.get("profile")
            if profile_id:
                profile_ids.append(profile_id)

        for profile_id in profile_ids:
            profile = get_tender_profile(self.request, profile_id, validate_status=("active",))

            profile_agreement_id = profile.get("agreementID")
            tender_agreement_id = tender_agreements[0].get("id")
            if profile_agreement_id != tender_agreement_id:
                raise_operation_error(
                    self.request,
                    "Tender agreement doesn't match profile agreement",
                    status=422,
                )

    def set_mode_test(self, tender):
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
            grouped_data[milestone.get("relatedLot")].append(milestone)

            if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM) and milestone.get("relatedLot"):
                related_lot_exists = True

        if tender_created_after(MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM):
            for lot, milestones in grouped_data.items():
                for i, milestone in enumerate(milestones):
                    if related_lot_exists and not milestone.get("relatedLot"):
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
                self.set_lot_guarantee(tender, lot)
                self.set_lot_value(tender, lot)
                self.set_lot_minimal_step(tender, lot)
                self.validate_minimal_step(lot, before)
                self.validate_lot_value(tender, lot)

    @staticmethod
    def set_lot_guarantee(tender: dict, lot: dict) -> None:
        if guarantee := lot.get("guarantee"):
            currency = tender["guarantee"]["currency"] if tender.get("guarantee") else guarantee.get("currency")
            lot["guarantee"]["currency"] = currency

    @staticmethod
    def set_lot_value(tender: dict, lot: dict) -> None:
        if tender_value := tender.get("value"):
            lot["value"].update(
                {
                    "currency": tender_value["currency"],
                    "valueAddedTaxIncluded": tender_value["valueAddedTaxIncluded"],
                }
            )

    @staticmethod
    def set_lot_minimal_step(tender: dict, lot: dict) -> None:
        if lot.get("minimalStep") and (tender_minimal_step := tender.get("minimalStep")):
            lot["minimalStep"].update(
                {
                    "currency": tender_minimal_step.get("currency"),
                    "valueAddedTaxIncluded": tender_minimal_step.get("valueAddedTaxIncluded"),
                }
            )

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
                self.request,
                "Minimal step value should be less than lot value",
                status=422,
                name="lots",
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
                    end_date = calculate_tender_full_date(
                        get_now(),
                        timedelta(days=qualif_complain_duration),
                        tender=after,
                    ).isoformat()

                    if qualif_complain_duration > 0:
                        for qualification in after["qualifications"]:
                            if qualification.get("status") in [
                                "unsuccessful",
                                "active",
                            ]:
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
        elif before["status"] == "active.pre-qualification.stand-still":
            block_stand_still_complaint_status = ("draft", "pending", "accepted")
            passed_data = get_request().validated["json_data"]
            if passed_data != {"status": "active.pre-qualification"}:
                raise_operation_error(
                    get_request(),
                    "Can't update tender at 'active.pre-qualification.stand-still' status",
                )

            lots = after.get("lots")
            if lots:
                active_lots = {lot["id"] for lot in lots if lot.get("status", "active") == "active"}
            else:
                active_lots = {None}

            if any(
                i["status"] in block_stand_still_complaint_status
                for q in after["qualifications"]
                for i in q.get("complaints", "")
                if q.get("lotID") in active_lots
            ):
                raise_operation_error(
                    get_request(),
                    "Can't switch to 'active.pre-qualification' before resolve all complaints",
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

    def initialize_enquiry_period(self, tender):
        if self.should_initialize_enquiry_period:
            if not self.enquiry_before_tendering:
                tender["enquiryPeriod"] = tender.get("enquiryPeriod") or {}
                tender["enquiryPeriod"]["startDate"] = tender["tenderPeriod"]["startDate"]
                tender["enquiryPeriod"]["endDate"] = calculate_tender_full_date(
                    dt_from_iso(tender["tenderPeriod"]["endDate"]),
                    self.enquiry_period_timedelta,
                    tender=tender,
                    working_days=self.tender_period_working_day,
                ).isoformat()

            clarification_until_duration = tender["config"]["clarificationUntilDuration"]
            if clarification_until_duration > 0:
                tender["enquiryPeriod"]["clarificationsUntil"] = calculate_tender_full_date(
                    dt_from_iso(tender["enquiryPeriod"]["endDate"]),
                    timedelta(days=clarification_until_duration),
                    tender=tender,
                    working_days=self.clarification_period_working_day,
                ).isoformat()

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

    def validate_required_criteria(self, before, after):
        if after.get("status") not in ("active", "active.enquiries", "active.tendering"):
            return

        rules = get_criteria_rules(after)

        mpc = after.get("mainProcurementCategory", MainProcurementCategory.SERVICES)

        # Load criteria rules
        required_criteria_ids = set()
        required_article_16_criteria_ids = set()

        for criterion_id, criterion_rules in rules.items():
            if "required" in criterion_rules["rules"]:
                required_criteria_ids.add(criterion_id)
            if "required_services" in criterion_rules["rules"] and mpc == MainProcurementCategory.SERVICES:
                required_criteria_ids.add(criterion_id)
            if "required_works" in criterion_rules["rules"] and mpc == MainProcurementCategory.WORKS:
                required_criteria_ids.add(criterion_id)
            if "required_article_16" in criterion_rules["rules"] and mpc in (
                MainProcurementCategory.WORKS,
                MainProcurementCategory.SERVICES,
            ):
                required_article_16_criteria_ids.add(criterion_id)

        # Gather tender criteria and item criteria
        tender_criteria_ids = set()
        item_criteria_ids = defaultdict(set)
        for criterion in after.get("criteria", ""):
            if criterion.get("classification"):
                tender_criteria_ids.add(criterion["classification"]["id"])
                if criterion.get("relatesTo") == "item":
                    related_item = criterion.get("relatedItem")
                    if related_item:
                        item_criteria_ids[related_item].add(criterion["classification"]["id"])

        # Check required criteria
        required_criteria_ids_diff = required_criteria_ids - tender_criteria_ids
        if required_criteria_ids_diff:
            raise_operation_error(
                get_request(),
                f"Tender must contain all required criteria: {', '.join(sorted(required_criteria_ids_diff))}",
            )

        # Check article 16 criteria if required
        if required_article_16_criteria_ids and not tender_criteria_ids.intersection(required_article_16_criteria_ids):
            raise_operation_error(
                get_request(),
                f"Tender must contain one of article 16 criteria: {', '.join(sorted(required_article_16_criteria_ids))}",
            )

        for item in after.get("items", []):
            market_obj = None
            # get profile for each tender criterion
            profile_is_active = False
            profile_id = item.get("profile")
            if profile_id:
                profile = get_tender_profile(self.request, profile_id)
                profile_is_active = profile.get("status", "active") == "active"
                if profile_is_active:
                    market_obj = profile

            # Skip validation if no market object is found
            if not market_obj:
                continue

            # get all criteria ids from market object
            market_criteria_ids = set()
            for market_criterion in market_obj.get("criteria", []):
                classification_id = market_criterion.get("classification", {}).get("id")
                if classification_id:
                    market_criteria_ids.add(classification_id)

            # check if all profile criteria are present for item
            market_criteria_ids_diff = market_criteria_ids - item_criteria_ids[item["id"]]
            if market_criteria_ids_diff:
                raise_operation_error(
                    get_request(),
                    f"Tender must contain all profile criteria for item {item['id']}: {', '.join(sorted(market_criteria_ids_diff))}",
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

        if tender.get("lots"):
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

        classifications = [item["classification"] for item in tender.get("items", "")]

        if not classifications:
            return

        validate_items_classifications_prefixes(classifications)

        if not self.should_validate_pre_selection_agreement:
            return

        agreements = tender.get("agreements")

        if not agreements:
            return

        agreement = get_object("agreement")

        if not agreement:
            return

        validate_items_classifications_prefixes(
            classifications,
            root_classification=agreement["classification"],
            root_name="agreement",
        )

    def validate_items_with_agreement(self, tender):
        """
        Validate items in tender is subset of items in agreement
        """
        COMPARE_FIELDS = (
            "description",
            "classification.scheme",
            "classification.id",
            "unit.code",
        )

        agreement = get_object("agreement")
        if not agreement or not agreement.get("items"):
            return

        def get_field_value(item, field):
            value = item
            for key in field.split("."):
                value = value.get(key, {})
            return value if not isinstance(value, dict) else None

        agreement_field_values = {
            field: {get_field_value(item, field) for item in agreement["items"]} for field in COMPARE_FIELDS
        }

        # Validate each tender item field is in agreement items
        for item in tender.get("items", []):
            for field in COMPARE_FIELDS:
                tender_value = get_field_value(item, field)
                if tender_value and tender_value not in agreement_field_values[field]:
                    raise_operation_error(
                        self.request,
                        f"Item {field} '{tender_value}' not found in agreement items",
                        status=422,
                        name="items",
                    )

        # Validate field combinations exist in agreement
        tender_combinations = {
            tuple(get_field_value(item, field) for field in COMPARE_FIELDS) for item in tender.get("items", [])
        }

        agreement_combinations = {
            tuple(get_field_value(item, field) for field in COMPARE_FIELDS) for item in agreement["items"]
        }

        invalid_combinations = tender_combinations - agreement_combinations
        if invalid_combinations:
            invalid_item = next(iter(invalid_combinations))
            raise_operation_error(
                self.request,
                "Item not found in agreement items: {}".format(invalid_item),
                status=422,
                name="items",
            )

    @classmethod
    def validate_items_classification_prefix_unchanged(cls, before, after):
        prefix_list = set()
        for item in before.get("items", ""):
            prefix_list.add(item["classification"]["id"][:CPV_GROUP_PREFIX_LENGTH])
        for item in after.get("items", ""):
            prefix_list.add(item["classification"]["id"][:CPV_GROUP_PREFIX_LENGTH])
        if len(prefix_list) != 1:
            prefix_name = CPV_PREFIX_LENGTH_TO_NAME[CPV_GROUP_PREFIX_LENGTH]
            raise_operation_error(
                get_request(),
                [f"Can't change classification {prefix_name} of items"],
                status=422,
                name="items",
            )

    def validate_tender_period_extension(self, tender):
        if "tenderPeriod" in tender and "endDate" in tender["tenderPeriod"]:
            tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
            if (
                calculate_tender_full_date(
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
        self.validate_tender_docs_confidentiality(documents)

    def validate_tender_docs_confidentiality(self, documents):
        for doc in documents:
            validate_edrpou_confidentiality_doc(doc)

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

    def has_insufficient_active_contracts(self, agreement):
        active_contracts_count = sum(c["status"] == "active" for c in agreement.get("contracts", ""))
        return active_contracts_count < self.agreement_min_active_contracts

    def has_mismatched_procuring_entities(self, tender, agreement):
        if not self.should_match_agreement_procuring_entity:
            return False

        agreement_identifier = agreement["procuringEntity"]["identifier"]
        tender_identifier = tender["procuringEntity"]["identifier"]
        return (
            tender_identifier["id"] != agreement_identifier["id"]
            or tender_identifier["scheme"] != agreement_identifier["scheme"]
        )

    def validate_related_lot_in_items(self, after):
        if (
            tender_created_after(RELATED_LOT_REQUIRED_FROM)
            or after.get("procurementMethodType") in [ABOVE_THRESHOLD, COMPETITIVE_ORDERING]
        ) and after["status"] != "draft":
            for item in after["items"]:
                if not item.get("relatedLot"):
                    raise_operation_error(
                        get_request(),
                        "This field is required",
                        status=422,
                        location="body",
                        name="item.relatedLot",
                    )

    def update_complaint_period(self, tender):
        if tender["config"]["hasTenderComplaints"] is not True:
            return
        if "tenderPeriod" not in tender or "endDate" not in tender["tenderPeriod"]:
            return
        if tender["config"]["tenderComplainRegulation"] == 0:
            return
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_tender_full_date(
            tendering_end,
            -timedelta(days=tender["config"]["tenderComplainRegulation"]),
            tender=tender,
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

    def validate_change_item_profile_or_category(self, after: dict, before: dict, force_validate: bool = False) -> None:
        after_cp = {}
        for item in after.get("items", []):
            after_cp[item["id"]] = {
                "profile": item.get("profile"),
                "category": item.get("category"),
            }

        before_cp = {}
        for item in before.get("items", []):
            before_cp[item["id"]] = {
                "profile": item.get("profile"),
                "category": item.get("category"),
            }

        request = get_request()

        for k, after_values in after_cp.items():
            before_values = before_cp.get(k, {})
            is_profile_changed = before_values.get("profile") != after_values.get("profile")
            is_category_changed = before_values.get("category") != after_values.get("category")

            if is_profile_changed or is_category_changed or force_validate:
                if (category_id := after_values.get("category")) is not None:
                    get_tender_category(request, category_id, ("active",))

                if (profile_id := after_values.get("profile")) is not None:
                    profile = get_tender_profile(request, profile_id, ("active",))

                    if profile.get("relatedCategory") != category_id:
                        raise_operation_error(request, "Profile should be related to category", status=422)

            if (is_profile_changed or is_category_changed) and before:
                self.cancel_all_technical_criteria(after, k)

    def cancel_all_technical_criteria(self, tender: dict, item_id: str) -> None:
        criteria_ids = (CRITERION_TECHNICAL_FEATURES, CRITERION_LOCALIZATION)
        now = get_now()
        for criterion in tender.get("criteria", ""):
            if (
                criterion.get("classification", {}).get("id") in criteria_ids
                and criterion.get("relatedItem") == item_id
            ):
                for rg in criterion.get("requirementGroups", ""):
                    for req in rg.get("requirements", ""):
                        req["status"] = ReqStatuses.CANCELLED
                        req["dateModified"] = now.isoformat()

    def invalidate_bids_data(self, tender):
        self.set_enquiry_period_invalidation_date(tender)
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"

    @staticmethod
    def set_enquiry_period_invalidation_date(tender):
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

    def validate_items_profile(self, tender):
        if (
            self.items_profile_required
            and tender.get("value", {}).get("amount", 0) > PROFILE_REQUIRED_MIN_VALUE_AMOUNT
            and tender.get("value", {}).get("currency") == "UAH"
            and tender.get("procuringEntity", {}).get("kind")
            not in (ProcuringEntityKind.SPECIAL, ProcuringEntityKind.DEFENSE, ProcuringEntityKind.OTHER)
        ):
            for item in tender["items"]:
                if not item.get("profile"):
                    raise_operation_error(
                        self.request,
                        [{"profile": ["This field is required."]}],
                        status=422,
                        name="items",
                    )

    def validate_contract_template_name(self, after, before):
        def raise_contract_template_name_error(message):
            raise_operation_error(
                self.request,
                message,
                status=422,
                location="body",
                name="contractTemplateName",
            )

        # Get tender status
        tender_before_status = before.get("status", "draft")
        tender_after_status = after.get("status", "draft")

        # Find if contractTemplateName is changed
        contract_template_name_before = before.get("contractTemplateName")
        contract_template_name = after.get("contractTemplateName")
        contract_template_name_changed = contract_template_name != contract_template_name_before

        # Check if contractTemplateName is allowed to be changed
        if contract_template_name_changed and not self.contract_template_name_patch_statuses:
            raise_contract_template_name_error("Rogue field")

        # Check if contractTemplateName is allowed to be changed in current tender status
        if contract_template_name_changed and tender_before_status not in self.contract_template_name_patch_statuses:
            raise_contract_template_name_error(
                f"Can't change contract template name in current tender '{tender_before_status}' status"
            )

        # Get all classification IDs from items
        classification_ids = set()
        for item in after.get("items", []):
            if item.get("classification") and item["classification"].get("id"):
                classification_ids.add(item["classification"]["id"])

        # Find if contractProforma is present
        tender_documents = after.get("documents", "")
        has_contract_proforma = any(i.get("documentType", "") == "contractProforma" for i in tender_documents)

        # Check if both contractTemplateName and contractProforma are present simultaneously
        if has_contract_proforma and contract_template_name:
            raise_contract_template_name_error(
                "Cannot use both contractTemplateName and contractProforma document simultaneously",
            )

        # Check if contractTemplateName or contractProforma is required
        if tender_after_status not in ("draft",) and self.contract_template_required:
            # FIXME: next if statement is temporary fix for already active tenders without contract template
            # TODO: remove this if later
            if tender_before_status in ("draft",) or contract_template_name_changed:
                # Check if either contractTemplateName or contractProforma is present
                if not has_contract_proforma and not contract_template_name:
                    raise_contract_template_name_error(
                        "Either contractTemplateName or contractProforma document is required"
                    )

        # If contractTemplateName is not specified, no further checks needed
        if not contract_template_name:
            return

        # Check if classifications is missing
        if not classification_ids:
            raise_contract_template_name_error("Can't set contractTemplateName for tender without classification")

        # Get expected template names for the classifications
        expected_template_names = get_contract_template_names_for_classification_ids(
            classification_ids,
            active_only=contract_template_name_changed,  # if unchanged - allow inactive templates
        )

        # Check if contractTemplateName is forbidden for excluded classifications
        if not expected_template_names:
            raise_contract_template_name_error(
                f"contractTemplateName is not allowed for current classifications {', '.join(sorted(classification_ids))}"
            )

        # Check if contractTemplateName is correct for the current classifications
        if contract_template_name not in expected_template_names:
            raise_contract_template_name_error(
                f"Incorrect contractTemplateName {contract_template_name} "
                f"for current classifications {', '.join(sorted(classification_ids))}, "
                f"use one of {', '.join(sorted(expected_template_names))}",
            )


class TenderDetailsMixing(TenderConfigMixin, BaseTenderDetailsMixing):
    pass


class TenderDetailsState(TenderDetailsMixing, TenderState):
    pass
